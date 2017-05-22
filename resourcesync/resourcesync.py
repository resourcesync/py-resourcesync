#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:samp:`Publish resources under the ResourceSync Framework`

The class :class:`ResourceSync` is the main entrance to the resourcesync library. It is in essence a one-method
class, its main method: :func:`~ResourceSync.execute`.

Upon execution :class:`ResourceSync` will call the correct :class:`~resourcesync.core.executors.Executor` that
will walk all the resource metadata provided by the implementation of the
:class:`~resourcesync.core.generator.Generator` and that takes care of creating the right type
of sitemap: resourcelist, changelist etc. and complete the corresponding
sitemaps as capabilitylist and description.

Before you call :func:`~ResourceSync.execute` on :class:`ResourceSync` it may be advisable to set the proper
parameters for your synchronization. :class:`ResourceSync` accepts arguments for
:class:`~resourcesync.parameters.parameters.Parameters` and the description of ``parameters`` in that class
is a good starting point to learn about the type, meaning and function of these parameters.
Here we will highlight some and discuss aspects of these parameters.

Providing resource metadata
---------------------------

The user of the library is responsible for providing the appropriate metadata needed for creating the ResourceSync
 documents. This component, called ``Generator``, will be responsible for providing the required metadata items to
  generate the ResourceSync documents.

This pluggable component must be a subclass of :class:`resourcesync.core.generator.Generator` and can be passed to the
``parameters`` class using the parameter name ``generator``. The ``Generator`` class has one method
:func:`~Generator.execute` that must be implemented by the pluggable component. This method requires the instance of
:class:`~resourcesync.parameters.parameters.Parameters` to be passed and returns a list of resource metadata. The
resource metadata must be instances of `:class:resync.Resource`.


Strategies and executors
------------------------

The :class:`~resourcesync.parameters.enum.Strategy` tells :class:`ResourceSync` in what way you want your resources
processed. Or better: :class:`ResourceSync` will choose the :class:`~resourcesync.core.executors.Executor` that fits
your chosen strategy. Do you want new resourcelists every time you call :func:`ResourceSync.execute`, do you want
new changelists or perhaps an incremental changelist. There are slots for other strategies in resourcesync,
such as resourcedump and changedump, but these strategies are not yet implemented.

If new changelist or incremental changelist is your strategy and there is no resourcelist.xml yet in your
:func:`~resourcesync.parameters.parameters.Parameters.metadata_dir` then :class:`ResourceSync` will create a
resourcelist.xml the first time you call :func:`~ResourceSync.execute`.

The :class:`~resourcesync.parameters.enum.Strategy` ``resourcelist`` does not require much system resources.
Resources will be processed one after the other and sitemap documents are written to disk once they are processed and
these sitemaps will at most take 50000 records. The strategies ``new_changelist`` and ``inc_changelist`` will
compare previous and present state of all your selected resources. In order to do so they collect metadata from
all the present resources in your selection and compare it to the previous state as recorded in resourcelists
and subsequent changelists.
This will be perfectly OK in most situations, however if the number of resources is very large this
comparison might be undoable. Anyway, large amounts of resources will probably be managed by some kind of
repository system that enables to query for the requested data. It is perfectly alright to write your own
:class:`~resourcesync.core.executors.Executor` that handles the synchronisation of resources in your repository system
and you are invited to share these executors. A suitable plugin mechanism to accommodate such extraterrestrial
executors could be accomplished in a next version of resourcesync.

.. seealso:: :func:`resourcesync.parameters.parameters.Parameters.strategy`,
:class:`resourcesync.parameters.enum.Strategy`, :doc:`resourcesync.core.executors <resourcesync.core.executors>`

Multiple collections
--------------------

:class:`ResourceSync` accepts and passes the arguments to :class:`~resourcesync.parameters.parameters.Parameters`
and so the parameters set on :class:`ResourceSync` can be saved and reinstituted later on.
:class:`~resourcesync.parameters.config.Configurations` has methods for listing and removing previously saved
configurations. Multiple collections of resources could be synchronized, each collection with its own configuration.
Synchronizing the collection 'spam' could go along these lines::

    # get a list of previously saved configurations
    [print(x) for x in Configurations.list_configurations()]
    # resourcesync
    # spam_config
    # eggs_config

    # import the custom generator component
    from resourcesync.generators.eg_generator import EgGenerator

    # prepare for synchronization of collection 'all about spam'
    resourcesync = ResourceSync(config_name="spam_config", generator=EgGenerator)

    # do the synchronization
    resourcesync.execute()


.. seealso:: :class:`resourcesync.parameters.parameters.Parameters`,
:class:`resourcesync.parameters.config.Configurations`,
:func:`~resourcesync.parameters.parameters.Parameters.save_configuration_as`

Observe execution
-----------------

:class:`ResourceSync` is a subclass of :class:`~resourcesync.util.observe.Observable`. The executor to which the
execution is delegated inherits all observers registered with :class:`ResourceSync`. :class:`ResourceSync` it self
does not fire events.

.. seealso::  :doc:`resourcesync.util.observe <resourcesync.util.observe>`,
:class:`resourcesync.core.executors.ExecutorEvent`

"""


import logging
from resourcesync.utils.observe import Observable
from resourcesync.rsxml.rsxml import RsXML
from resourcesync.parameters.enum import Strategy
from resourcesync.executor.resourcelist import ResourceListExecutor
from resourcesync.executor.changelist import IncrementalChangeListExecutor, NewChangeListExecutor
from resourcesync.core.generator import get_generator
from resourcesync.parameters.parameters import Parameters


LOG = logging.getLogger(__name__)


class ResourceSync(Observable):
    """
    :samp: Main class for publishing ResourceSync documents.
    """

    def __init__(self, **kwargs):
        self.rsxml = RsXML()
        Observable.__init__(self)
        self.params = Parameters(**kwargs)
        LOG.debug("ResourceSync initialized with the configuration provided.")

    def execute(self):

        executor = None
        if self.params.strategy == Strategy.resourcelist:
            executor = ResourceListExecutor(parameters=self.params)
        elif self.params.strategy == Strategy.new_changelist:
            executor = NewChangeListExecutor(parameters=self.params)
        elif self.params.strategy == Strategy.inc_changelist:
            executor = IncrementalChangeListExecutor(parameters=self.params)
        else:
            raise NotImplementedError("Strategy %s not implemented" % self.params.strategy)

        LOG.debug("Found executor for the strategy %s." % self.params.strategy)
        LOG.debug("Obtaining list of resource metadata from the generator.")
        resource_metadata = self.get_resource_list()

        if executor:
            executor.execute(resource_metadata)

        self.params.save_configuration(True)

    def get_resource_list(self):

        generator_name = self.params.generator
        LOG.debug("Generator name provided in the configuration: %s" % generator_name)
        Generator = get_generator(generator_name)
        if not Generator:
            raise NotImplementedError("No Generator found with name: %s" % generator_name)
        generator = Generator(self.params)
        LOG.debug("Generator found. Obtaining resources.")
        resource_metadata = generator.generate()

        if not resource_metadata:
            # is returning no metadata an error?
            LOG.warning("Generator returned an empty list of resource metadata")
            return
        return resource_metadata


