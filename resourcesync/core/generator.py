# -*- coding: utf-8 -*-

"""
:samp:`The Generator base class.`
"""

from resync import Resource
from abc import ABCMeta
import logging


class GeneratorMount(type):

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.plugins.append(cls)


class Generator(metaclass=GeneratorMount):

    def __init__(self, params, rsxml=None):
        self.params = params
        self.rsxml = rsxml

    def __get_logger(self):
        logger = logging.getLogger(__name__)

    def generate(self) -> [Resource]:
        raise NotImplementedError("Generator not implemented")


class Filter(object, metaclass=ABCMeta):

    def execute(self) -> [Resource]:
        raise NotImplementedError


class Selector(object, metaclass=ABCMeta):

    def execute(self) -> [Resource]:
        raise NotImplementedError


def get_generator(generator_name):
    import resourcesync.generators as gen_plugins
    import os
    for module in os.listdir(os.path.dirname(gen_plugins.__file__)):
        if module == "__init__.py" or not module.endswith(".py"):
            continue
        __import__(gen_plugins.__name__ + "." + module[:-3], locals(), globals())

    log = logging.getLogger(__name__)
    log.debug("Finding generator with name %s" % generator_name)
    if generator_name:
        for gen in Generator.plugins:
            if gen.__name__ == generator_name:
                log.debug("Generator found: %s" % gen.__name__)
                return gen
    log.debug("No generator found with name %s" % generator_name)
