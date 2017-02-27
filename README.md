# py-resourcesync


Core Python library for ResourceSync publishing

---
- The component in this repository is intended to be used by developers and/or system administrators.
- Source location: [https://github.com/resourcesync/py-resourcesync](https://github.com/resourcesync/py-resourcesync)
- In case of questions [contact here](https://github.com/resourcesync/py-resourcesync/issues/new).

---

## Introduction
The [ResourceSync specification](http://www.openarchives.org/rs/1.0.9/resourcesync) describes 
a synchronization framework for the web consisting of various capabilities that allow third-party systems to remain synchronized with a server's evolving resources.
More precisely the ResourceSync Framework describes the communication between `source` and `destination` aimed at
synchronizing one or more resources. Communication uses `http` and an extension on 
the [Sitemap protocol](http://www.sitemaps.org/protocol.html), an xml-based format for expressing metadata, relevant for synchronization.

The software in `py-resourcesync` library handles the `source`-side implementation of the framework.
Given a bunch of resources it analyzes these resources and the differences over time and creates
the necessary sitemap-documents that describe the resources and the changes. 

## Overview

![Overview](img/comp_02.png)

_Fig. 1. Overview of the main features of `py-resourcesync`._

In essence py-resourcesync is a one-class, one-method library: class `ResourceSync`, method `execute`.
But there is more:

- `Parameters` control the conditions under which the execution takes place. Multiple sets of parameters can
be saved as configurations and restored from disk.
- The set of resources that will be synchronized can be selected and filtered using pluggable component
called `Generator`. The user can easily implement ways to select and filter metadata for resources for your system.
    - The `execute` method in the `ResourceSync` class will invoke the `generate` function of the custom 
    generator to retrieve the resource metadata. The custom generator must be a subclass of the `Generator` class.
    - The generator is responsible for selecting and filtering the necessary resources and gathering the 
    required metadata needed to build the ResourceSync documents.
    - The generator must return a list of [resync/Resource](https://github.com/resync/resync/blob/master/resync/resource.py) 
    instances when the called by the `ResourceSync.execute` method.
- The chosen `Strategy` determines what kind of process will do the synchronization. At the moment there are `Executors`
that produce _resourcelists_, _new changelists_ or _incremental changelists_.

A set of parameters, known as a configuration, can precisely define a set of resources, the selection and filter
mechanisms, the publication strategy and where to store the resourcesync metadata. Dedicated configurations can be defined
for multiple sets of resources and published in equal amounts of _capabilitylists_. A configuration can be saved on disk,
restored and run with a minimum effort. This makes `py-resourcesync` the ideal library for scripting a publication
strategy that will serve multiple groups of consumers that may be interested in different sets of resources offered
by your site.


## Quick install

### Running from source
Clone or downoad the source code. If your editor does not install required packages, issue the pip install
command from the root directory of this project.
```
$ cd your/path/to/py-resourcesync
$ python setup.py install
```

