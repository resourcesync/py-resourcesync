# -*- coding: utf-8 -*-

"""
:samp:`The selector base class. Not fully defined yet.`
"""

from abc import ABCMeta, abstractmethod
from resync import Resource


class Selector(object, metaclass=ABCMeta):

    def execute(self) -> [Resource]:
        raise NotImplementedError
