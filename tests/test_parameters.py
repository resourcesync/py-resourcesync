# -*- coding: utf-8 -*-

from .context import Parameters
import unittest


class ParametersTest(unittest.TestCase):

    def test_generator(self):
        with self.assertRaises(ValueError):
            params = Parameters(generator="Generator")

        params = Parameters(generator="resourcesync.generators.eg_generator.EgGenerator")
        params.describe(as_string=True)
        print(params.generator.__name__)
        params.generator(params)


if __name__ == "__main__":
    unittest.main()
