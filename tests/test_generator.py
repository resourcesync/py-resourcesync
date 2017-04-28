# -*- coding: utf-8 -*-

#from .context import Generator, RsXML, Parameters
from resourcesync.core.generator import Generator
from resourcesync.parameters.parameters import Parameters
import unittest


class GeneratorTest(unittest.TestCase):

    def test_constructor(self):
        params = Parameters()
        gen = Generator(params=params)
        assert isinstance(gen, Generator)
        with self.assertRaises(NotImplementedError):
            gen.generate()
        assert len(Generator.plugins) > 0


if __name__ == "__main__":
    unittest.main()