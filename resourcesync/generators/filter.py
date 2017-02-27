# -*- coding: utf-8 -*-

"""
:samp:`The Filter base class. Not fully defined yet.`
"""

from abc import ABCMeta, abstractmethod
from resync import Resource


class Filter(object, metaclass=ABCMeta):

    def execute(self) -> [Resource]:
        raise NotImplementedError
