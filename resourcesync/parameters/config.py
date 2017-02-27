# -*- coding: utf-8 -*-

"""
:samp:`Save and load multiple configurations`

The class :class:`Configurations` (mark the `s` at the end) enables you to save, load, remove and list
multiple configurations.

Class :class:`Configuration` (mark the absence of `s` at the end) is a singleton.
It should not be used directly. In stead use :class:`rspub.core.rs_paras.RsParameters`.

The location where configurations are stored is system-dependent:

 - ``{user-home}\\AppData\\Local\\Programs\\rspub\\config\\`` on Windows
 - ``{user-home}/.config/rspub/config/`` on Mac and Linux
 - ``{user-home}/rspub/config/`` fallback

.. seealso:: :doc:`RsParameters <rspub.core.rs_paras>`

"""

import logging
import os
import platform
from configparser import ConfigParser
from glob import glob

from resourcesync.parameters.enum import Strategy, SelectMode

CFG_FILENAME = "DEFAULT.cfg"
CFG_DIRNAME = "core"
SECTION_CORE = "core"
EXT = ".cfg"


class Configurations(object):
    """
    :samp:`Enables saving, loading, listing and removing {configurations}`

    All methods are static::

        Configurations.list_configurations()
        Configurations.load_configuration("collection_1")
        # etc.

    """
    @staticmethod
    def __get__logger():
        logger = logging.getLogger(__name__)
        return logger

    @staticmethod
    def list_configurations() -> list:
        """
        :samp:`List available configurations`

        :return: list of names of previously saved configurations
        """
        config_path = Configuration._get_config_path()
        config_files = sorted(glob(os.path.join(config_path, "*" + EXT)))
        return [os.path.splitext(os.path.basename(x))[0] for x in config_files]

    @staticmethod
    def load_configuration(name: str):
        """
        :samp:`Load the configuration with the given name`

        :param name: name of a previously saved configuration
        :return: the restored Configuration
        """
        if name not in Configurations.list_configurations():
            raise ValueError("No configuration named '%s'" % name)
        Configuration.reset()
        Configuration._set_configuration_filename(name + EXT)
        Configurations.__get__logger().info("Loaded configuration %s" % name)
        return Configuration()

    @staticmethod
    def save_configuration_as(name: str):
        """
        :samp:`Save the current configuration under the given name`

        Any previously saved configurations with the same name will be overwritten without warning.

        :param name: name under which the configuration will be saved
        """
        if name is None or name == "":
            raise ValueError("Invalid configuration name. (None or empty string)")
        nam = os.path.splitext(name)[0]
        config_path = Configuration._get_config_path()
        config_file = os.path.join(config_path, nam + EXT)
        current_cfg = Configuration()
        current_cfg.config_file = config_file
        current_cfg.persist()
        Configurations.__get__logger().info("Saved configuration %s" % name)

    @staticmethod
    def remove_configuration(name: str):
        """
        :samp:`Remove the configuration with the given name`

        :param name: the name of the configuration to remove
        :return: **True** if the configuration was successfully removed, **False** otherwise
        """
        if name is None or name == "":
            raise ValueError("Invalid configuration name '%s'", name)
        nam = os.path.splitext(name)[0]
        config_path = Configuration._get_config_path()
        config_file = os.path.join(config_path, nam + EXT)
        if os.path.exists(config_file):
            os.remove(config_file)
            Configurations.__get__logger().info("Removed configuration %s" % name)
            return True
        else:
            return False

    @staticmethod
    def current_configuration_name():
        """
        :samp:`Get the name of the current configuration`

        :return: name of the current configuration
        """
        current_cfg = Configuration()
        return os.path.splitext(os.path.basename(current_cfg.config_file))[0]

    @staticmethod
    def rspub_config_dir():
        current_cfg = Configuration()
        return os.path.dirname(os.path.dirname(current_cfg.config_file))


class Configuration(object):
    """
    :samp:`Singleton persisting object for storing configuration parameters`

    .. warning::

        Do not use class Configuration directly. Use :doc:`Parameters <resourcesync.parameters.parameters>` instead.

    """

    _configuration_filename = CFG_FILENAME

    @staticmethod
    def __get__logger():
        logger = logging.getLogger(__name__)
        return logger

    @staticmethod
    def _set_configuration_filename(cfg_filename):
        Configuration.__get__logger().debug("Setting configuration filename to %s", cfg_filename)
        Configuration._configuration_filename = cfg_filename

    @staticmethod
    def _get_configuration_filename():
        if not Configuration._configuration_filename:
            Configuration._set_configuration_filename(CFG_FILENAME)

        return Configuration._configuration_filename

    @staticmethod
    def reset():
        Configuration._instance = None
        Configuration.__get__logger().debug("Configuration was reset.")

    @staticmethod
    def _get_config_path():

        c_path = os.path.expanduser("~")
        opsys = platform.system()
        if opsys == "Windows":
            win_path = os.path.join(c_path, "AppData", "Local")
            if os.path.exists(win_path): c_path = win_path
        elif opsys == "Darwin":
            dar_path = os.path.join(c_path, ".config")
            if not os.path.exists(dar_path): os.makedirs(dar_path)
            if os.path.exists(dar_path): c_path = dar_path
        elif opsys == "Linux":
            lin_path = os.path.join(c_path, ".config")
            if not os.path.exists(lin_path): os.makedirs(lin_path)
            if os.path.exists(lin_path): c_path = lin_path

        c_path = os.path.join(c_path, "rspub", CFG_DIRNAME)
        if not os.path.exists(c_path):
            os.makedirs(c_path)
        #Configuration.__get__logger().info("Configuration directory: %s", c_path)
        return c_path

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            Configuration.__get__logger().debug("Creating Configuration._instance")
            cls._instance = super(Configuration, cls).__new__(cls, *args)
            cls.config_path = cls._get_config_path()
            cls.config_file = os.path.join(cls.config_path, Configuration._get_configuration_filename())
            cls.parser = ConfigParser()
            if os.path.exists(cls.config_file):
                cls.parser.read(cls.config_file, encoding="utf-8")
        return cls._instance

    def config_path(self):
        return self.config_path

    def config_file(self):
        return self.config_file

    def name(self):
        return os.path.splitext(os.path.basename(self.config_file))[0]

    def persist(self):
        f = open(self.config_file, "w", encoding="utf-8")
        self.parser.write(f)
        f.close()
        Configuration.__get__logger().debug("Persisted %s", self.config_file)

    def __set_option__(self, section, option, value):
        if not self.parser.has_section(section):
            self.parser.add_section(section)
        if value is None:
            self.parser.remove_option(section, option)
        else:
            self.parser.set(section, option, value)

    def __get_int__(self, section, option, fallback=0):
        value = self.parser.get(section, option, fallback=str(fallback))
        return int(value)

    def __set_int__(self, section, option, value):
        self.__set_option__(section, option, str(value))

    def __get_boolean__(self, section, option, fallback=True):
        value = self.parser.get(section, option, fallback=str(fallback))
        return not(value == "False" or value == "None")

    def __set_boolean__(self, section, option, value):
        self.__set_option__(section, option, str(value))

    def core_items(self):
        return self.parser.items(SECTION_CORE)

    def core_clear(self):
        self.parser.remove_section(SECTION_CORE)

    # core settings
    def resource_dir(self, fallback=os.path.expanduser("~")):
        return self.parser.get(SECTION_CORE, "resource_dir", fallback=fallback)

    def set_resource_dir(self, resource_dir):
        self.__set_option__(SECTION_CORE, "resource_dir", resource_dir)

    def metadata_dir(self, fallback="metadata"):
        return self.parser.get(SECTION_CORE, "metadata_dir", fallback=fallback)

    def set_metadata_dir(self, metadata_dir):
        self.__set_option__(SECTION_CORE, "metadata_dir", metadata_dir)

    def description_dir(self, fallback=None):
        return self.parser.get(SECTION_CORE, "description_dir", fallback=fallback)

    def set_description_dir(self, description_dir):
        self.__set_option__(SECTION_CORE, "description_dir", description_dir)

    def selector_file(self, fallback=None):
        return self.parser.get(SECTION_CORE, "selector_file", fallback=fallback)

    def set_selector_file(self, selector_file):
        self.__set_option__(SECTION_CORE, "selector_file", selector_file)

    def simple_select_file(self, fallback=None):
        return self.parser.get(SECTION_CORE, "simple_select_file", fallback=fallback)

    def set_simple_select_file(self, simple_file):
        self.__set_option__(SECTION_CORE, "simple_select_file", simple_file)

    def select_mode(self, fallback=SelectMode.simple.name):
        return SelectMode[self.parser.get(SECTION_CORE, "select_mode", fallback=fallback)]

    def set_select_mode(self, mode):
        self.__set_int__(SECTION_CORE, "select_mode", mode.name)

    def plugin_dir(self, fallback=None):
        return self.parser.get(SECTION_CORE, "plugin_dir", fallback=fallback)

    def set_plugin_dir(self, plugin_dir):
        self.__set_option__(SECTION_CORE, "plugin_dir", plugin_dir)

    def history_dir(self, fallback=None):
        return self.parser.get(SECTION_CORE, "history_dir", fallback=fallback)

    def set_history_dir(self, history_dir):
        self.__set_option__(SECTION_CORE, "history_dir", history_dir)

    def url_prefix(self, fallback="http://www.example.com"):
        return self.parser.get(SECTION_CORE, "url_prefix", fallback=fallback)

    def set_url_prefix(self, urlprefix):
        self.__set_option__(SECTION_CORE, "url_prefix", urlprefix)

    def document_root(self, fallback="/var/www/html/"):
        return self.parser.get(SECTION_CORE, "document_root", fallback=fallback)

    def set_document_root(self, document_root):
        self.__set_option__(SECTION_CORE, "document_root", document_root)

    def generator(self, fallback="resourcesync.core.generator.Generator"):
        return self.parser.get(SECTION_CORE, "generator", fallback=fallback)

    def set_generator(self, generator):
        # saving the module + name of the generator class, which can be converted back to
        # python class when re-loading this config
        gen_name = generator.__module__ + "." + generator.__name__
        self.__set_option__(SECTION_CORE, "generator", gen_name)

    def strategy(self, fallback=Strategy.resourcelist.name):
        return Strategy[self.parser.get(SECTION_CORE, "strategy", fallback=fallback)]

    def set_strategy(self, strategy):
        self.__set_option__(SECTION_CORE, "strategy", strategy.name)

    def max_items_in_list(self, fallback=50000):
        return self.__get_int__(SECTION_CORE, "max_items_in_list", fallback)

    def set_max_items_in_list(self, max_items):
        self.__set_int__(SECTION_CORE, "max_items_in_list", max_items)

    def zero_fill_filename(self, fallback=4):
        return self.__get_int__(SECTION_CORE, "zero_fill_filename", fallback)

    def set_zero_fill_filename(self, zfill):
        self.__set_int__(SECTION_CORE, "zero_fill_filename", zfill)

    def is_saving_pretty_xml(self, fallback=True):
        return self.__get_boolean__(SECTION_CORE, "is_saving_pretty_xml", fallback)

    def set_is_saving_pretty_xml(self, p_xml):
        self.__set_boolean__(SECTION_CORE, "is_saving_pretty_xml", p_xml)

    def is_saving_sitemaps(self, fallback=True):
        return self.__get_boolean__(SECTION_CORE, "is_saving_sitemaps", fallback)

    def set_is_saving_sitemaps(self, is_saving):
        self.__set_boolean__(SECTION_CORE, "is_saving_sitemaps", is_saving)

    def has_wellknown_at_root(self, fallback=True):
        return self.__get_boolean__(SECTION_CORE, "has_wellknown_at_root", fallback)

    def set_has_wellknown_at_root(self, at_root):
        self.__set_boolean__(SECTION_CORE, "has_wellknown_at_root", at_root)

    def last_excution(self):
        return self.parser.get(SECTION_CORE, "last_excution", fallback=None)

    def set_last_execution(self, date_string):
        self.__set_option__(SECTION_CORE, "last_excution", date_string)
