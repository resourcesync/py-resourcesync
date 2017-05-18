# -*- coding: utf-8 -*-

from resourcesync.parameters.parameters import Parameters
import unittest
import logging

#logging.getLogger(__name__)
#logging.basicConfig(level=logging.DEBUG)


class ParametersTest(unittest.TestCase):

    def assert_params(self, params: Parameters):
        assert params.resource_dir is not None
        assert params.metadata_dir is not None
        #assert params.description_dir is not None
        assert params.url_prefix is not None
        assert params.document_root is not None
        assert params.strategy is not None
        #assert params.generator is not None
        assert params.max_items_in_list > 0
        assert params.zero_fill_filename > 0

    def test_kwargs(self):
        params = Parameters(new_param="ss")
        assert params.new_param == 'ss'

    def test_defaults(self):
        #with self.assertRaises(ValueError):
        #    params = Parameters(generator="Generator")

        params = Parameters()
        self.assert_params(params)

    def test_resource_dir(self):
        params = Parameters(resource_dir="/etc")
        self.assert_params(params)

        with self.assertRaises(AssertionError):
            Parameters(resource_dir=1111)

        with self.assertRaises(ValueError):
            Parameters(resource_dir="XXXX")

        with self.assertRaises(ValueError):
            Parameters(resource_dir="/etc/bashrc")

    def test_metadata_dir(self):
        params = Parameters(metadata_dir="rs_metadata")
        self.assert_params(params)

        with self.assertRaises(ValueError):
            Parameters(metadata_dir="")

        with self.assertRaises(ValueError):
            Parameters(metadata_dir="/etc/metadata")

    def test_description_dir(self):
        params = Parameters(description_dir="/etc")
        self.assert_params(params)

        with self.assertRaises(AssertionError):
            Parameters(description_dir=1)

        with self.assertRaises(ValueError):
            Parameters(description_dir="XXXX")

        with self.assertRaises(ValueError):
            Parameters(description_dir="/etc/bashrc")

    def test_url_prefix(self):
        params = Parameters(url_prefix="http://www.resourcesync.org/")
        self.assert_params(params)

        with self.assertRaises(ValueError):
            Parameters(url_prefix="//www.resourcesync.org")

        with self.assertRaises(ValueError):
            Parameters(url_prefix="http://safsfaasdgasf")

        with self.assertRaises(ValueError):
            Parameters(url_prefix="http://localhost")

        with self.assertRaises(ValueError):
            Parameters(url_prefix="http://:9000")

    def test_document_root(self):
        params = Parameters(document_root="/var/www/html")
        self.assert_params(params)

        with self.assertRaises(ValueError):
            Parameters(document_root="")

    def test_strategy(self):
        Parameters(strategy=0)
        Parameters(strategy=1)
        Parameters(strategy=2)

        Parameters(strategy="resourcelist")
        Parameters(strategy="new_changelist")
        Parameters(strategy="inc_changelist")
        # id strategy is none, the default will be picked
        Parameters(strategy=None)

        with self.assertRaises(ValueError):
            Parameters(strategy="sfasdadasdsa")

        with self.assertRaises(ValueError):
            Parameters(strategy=100)

    def test_generator(self):
        Parameters(generator="EgGenerator")

        with self.assertRaises(TypeError):
            Parameters(generator=1111)

    def test_max_items_in_list(self):
        Parameters(max_items_in_list=1000)
        Parameters(max_items_in_list=None)

        with self.assertRaises(ValueError):
            Parameters(max_items_in_list=100000)

        with self.assertRaises(ValueError):
            Parameters(max_items_in_list="ssssss")

    def test_zero_fill_filename(self):
        Parameters(zero_fill_filename=2)

        with self.assertRaises(ValueError):
            Parameters(zero_fill_filename=20)

        with self.assertRaises(ValueError):
            Parameters(zero_fill_filename="ggg")

    def test_is_saving_pretty_xml(self):
        Parameters(is_saving_pretty_xml=True)
        with self.assertRaises(TypeError):
            Parameters(is_saving_pretty_xml="fff")

    def test_is_saving_sitemaps(self):
        Parameters(is_saving_sitemaps=True)
        with self.assertRaises(TypeError):
            Parameters(is_saving_sitemaps=111)

    def test_has_wellknown_at_root(self):
        Parameters(has_wellknown_at_root=True)
        with self.assertRaises(TypeError):
            Parameters(has_wellknown_at_root="asssssfasfda")


if __name__ == "__main__":
    unittest.main()
