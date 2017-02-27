# -*- coding: utf-8 -*-

from .context import Generator, RsXML, Parameters
import unittest


class GeneratorTest(unittest.TestCase):

    def test_constructor(self):
        params = Parameters()
        gen = Generator(params=params)
        print(gen.__class__)
        print(gen.params.__class__)

if __name__ == "__main__":
    unittest.main()