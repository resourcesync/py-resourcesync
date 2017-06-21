# -*- coding: utf-8 -*-

"""
:samp:`The Generator base class.`
"""

from resync import Resource
from abc import ABCMeta
import logging


class Generator():

    def __init__(self, params=None, rsxml=None):
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
