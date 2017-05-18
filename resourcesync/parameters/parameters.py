# -*- coding: utf-8 -*-

import validators
import os
import urllib.parse
from resourcesync.parameters.enum import Strategy
from numbers import Number
from resourcesync.utils import defaults
import logging
from glob import glob
from configparser import ConfigParser
import platform

WELL_KNOWN_PATH = os.path.join(".well-known", "resourcesync")
WELL_KNOWN_URL = ".well-known/resourcesync"
config = None
CFG_FILENAME = "DEFAULT.cfg"
CFG_DIRNAME = "core"
SECTION_CORE = "core"
EXT = ".cfg"


class ParameterUtils(object):
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
        config_path = Parameters._get_config_path()
        config_files = sorted(glob(os.path.join(config_path, "*" + EXT)))
        return [os.path.splitext(os.path.basename(x))[0] for x in config_files]

    @staticmethod
    def load_configuration(name: str):
        """
        :samp:`Load the configuration with the given name`

        :param name: name of a previously saved configuration
        :return: the restored Configuration
        """
        if name not in ParameterUtils.list_configurations():
            raise ValueError("No configuration named '%s'" % name)
        Parameters.reset()
        Parameters._set_configuration_filename(name + EXT)
        ParameterUtils.__get__logger().info("Loaded configuration %s" % name)
        return Parameters()

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
        config_path = Parameters._get_config_path()
        config_file = os.path.join(config_path, nam + EXT)
        current_cfg = Parameters()
        current_cfg.config_file = config_file
        current_cfg.persist()
        ParameterUtils.__get__logger().info("Saved configuration %s" % name)

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
        config_path = Parameters._get_config_path()
        config_file = os.path.join(config_path, nam + EXT)
        if os.path.exists(config_file):
            os.remove(config_file)
            ParameterUtils.__get__logger().info("Removed configuration %s" % name)
            return True
        else:
            return False

    @staticmethod
    def current_configuration_name():
        """
        :samp:`Get the name of the current configuration`

        :return: name of the current configuration
        """
        current_cfg = Parameters()
        return os.path.splitext(os.path.basename(current_cfg.config_file))[0]

    @staticmethod
    def rspub_config_dir():
        current_cfg = Parameters()
        return os.path.dirname(os.path.dirname(current_cfg.config_file))

    @staticmethod
    def _assert_directory(path, arg):
        assert isinstance(path, str)
        if path == "~":
            path = os.path.expanduser(path)
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        if not os.path.exists(path):
            raise ValueError("Invalid value for %s: path does not exist: %s" % (arg, path))
        elif not os.path.isdir(path):
            raise ValueError("Invalid value for %s: not a directory: %s" % (arg, path))
        return path

    @staticmethod
    def _assert_max_number(n, min, max, arg):
        if not isinstance(n, Number):
            raise ValueError("Invalid value for %s: not a number %s" % (arg, n))
        if not min <= n <= max:
            raise ValueError("Invalid value for %s: value should be between %d and %d" % (arg, min, max))
        return True

    @staticmethod
    def get_resource_dir(path):
        assert isinstance(path, str)
        path = ParameterUtils._assert_directory(path, "resource_dir")
        if not (path.endswith(os.path.sep) or path.endswith("\\") or path.endswith("/")):
            path += os.path.sep
        return path

    @staticmethod
    def get_metadata_dir(path):
        if os.path.isabs(path):
            raise ValueError("Invalid value for metadata_dir: path should not be absolute: %s" % path)
        if path is None or path == "":
            raise ValueError("Invalid value for metadata_dir: path should not be empty")
        return path

    @staticmethod
    def get_description_dir(path):
        if path:
            path = ParameterUtils._assert_directory(path, "description_dir")
        return path

    @staticmethod
    def get_url_prefix(value):
        if value.endswith("/"):
            value = value[:-1]
        parts = urllib.parse.urlparse(value)
        if parts[0] not in ["http", "https"]:  # scheme
            raise ValueError("URL schemes allowed are 'http' or 'https'. Given: '%s'" % value)
        is_valid_domain = validators.domain(parts[1])  # netloc
        if not is_valid_domain:
            raise ValueError("URL has invalid domain name: '%s'. Given: '%s'" % (parts[1], value))
        if parts[4] != "":  # query
            raise ValueError("URL should not have a query string. Given: '%s'" % value)
        if parts[5] != "":  # fragment
            raise ValueError("URL should not have a fragment. Given: '%s'" % value)
        is_valid_url = validators.url(value)
        if not is_valid_url:
            raise ValueError("URL is invalid. Given: '%s'" % value)
        if not value.endswith("/"):
            value += "/"
        return value

    @staticmethod
    def get_document_root(value):
        if value.endswith("/"):
            value = value[:-1]
        if value == "":
            raise ValueError("Invalid value for document_root: path should not be empty")
        if not value.endswith("/"):
            value += "/"
        return value

    @staticmethod
    def get_strategy(value):
        return Strategy.strategy_for(value)

    @staticmethod
    def get_history_dir(path):
        if path and not isinstance(path, str):
            raise ValueError("Value for history_dir should be string. %s is %s" % (path, type(path)))
        if path == "":
            path = None
        return path

    @staticmethod
    def get_plugin_dir(path):
        if path:
            path = ParameterUtils._assert_directory(path, "plugin_dir")
        return path

    @staticmethod
    def assert_max_items_in_list(max_items):
        return ParameterUtils._assert_max_number(max_items, 1, 50000, "max_items_in_list")

    @staticmethod
    def assert_zero_fill_filename_range(zfill):
        return ParameterUtils._assert_max_number(zfill, 1, 10, "zero_fill_filename")


class Parameters(object):
    """
    :samp: Handles the parameters necessary for generating and publishing ResoruceSync documents.

    Parameters can be set in the :func:`__init__` method of this class and as properties. Each parameter gets a
    screening on validity and a `ValueError` will be raised if it is not valid. Parameters can be saved collectively
    as a configuration. Multiple named configurations can be stored by using the method :func:`save_configuration_as`.
    Named configurations can be restored by giving the `config_name` at initialisation::

        # params is an instance of Parameters with configuration adequately set for collection 1
        # it is saved as 'collection_1_config':
        params.save_configuration_as("collection_1_config")

        # ...
        # Later on it is restored...
        params = Parameters(config_name="collection_1_config")

    Parameters can be cloned::

        # params1 is an instance of Parameters
        params2 = Parameters(**params1.__dict__)
        params1 == params2    # False
        params1.__dict__ == params2.__dict__  # True

    Besides parameters the Parameters class also has methods for derived properties.

    :samp:
    All ``parameters`` will get their value from

    1. the _named argument in `\*\*kwargs`. (this is for cloning instances of RsParameters). If not available:
    2. the named argument. If not available:
    3. the parameter as saved in the current configuration. If not available:
    4. the default configuration value.

    :param str config_name: the name of the configuration to read. If given, sets the current configuration.
    :param str resource_dir: ``parameter`` :param:`resource_dir`
        ``parameter`` :samp:`The local root directory for ResourceSync publishing` (str)

        The given value should point to an existing directory. A relative path will be made absolute, calculated
        from the current working directory (`os.getcwd()`).

        The resource_dir acts as the root of the resources to be published. The urls to the resources are
        calculated relative to the resource_dir. Example::

        resourece_dir:  /abs/path/to/resource_dir
        resource:       /abs/path/to/resource_dir/sub/path/to/resource
        url:                        url_prefix + /sub/path/to/resource

        ``default:`` user home directory
        See also: :param:`url_prefix`
        
    :param str metadata_dir: ``parameter`` :param:`metadata_dir`
        ``parameter`` :samp:`The directory for ResourceSync documents` (str)

        The metadata_dir is the directory where sitemap documents will be saved.
        Names and relative path names are allowed. An absolute path will raise a
        :exc:`ValueError`.

        The metadata directory will be calculated relative to the :param:`resource_dir`.

        If the metadata directory does not exist it will be created during execution of a synchronization.
        ``default:`` 'metadata'
        See also: :param:`abs_metadata_dir`
        
    :param str description_dir: ``parameter`` :param:`description_dir`
        ``parameter`` :samp:`Directory where a version of the description document is kept` (str)

        The description document, also known as `.well-known/resourcesync`, is keeping links to the
        capability list(s) at the site. A local copy of the description document (or the real description
        document if synchronization takes place at the server) will be updated with newly created
        capability lists. The `description_dir` should point to a directory where the
        :samp:`.well-known/resourcesync` document can be found.

        If `description_dir` is **None** the :param:`abs_metadata_dir` will be taken as `description_dir`.

        If the document :samp:`{{description_dir}}/.well-known/resourcesync` does not exist it will be created.

        ``default:`` **None**

        See also: :param:`abs_description_path`
        
    :param str url_prefix: ``parameter`` :param:`url_prefix`
        ``parameter`` :samp:`The URL-prefix for ResourceSync publishing` (str)

        The url_prefix substitutes :param:`resource_dir` when calculating urls to resources. The `url_prefix`
        should be the host name of the server or host name + path that points to the root directory of the
        resources. `url_prefix + relative/path/to/resource` should yield a valid url.

        Example. Paths to resources are relative to the server host::

            path to resource:           {resource_dir}/path/to/resource
            url_prefix:         http://www.example.com
            url to resource:    http://www.example.com/path/to/resource
        Example. Paths to resources are relative to some directory on the server::

            path to resource:                        {resource_dir}/path/to/resource
            url_prefix:         http://www.example.com/my/resources
            url to resource:    http://www.example.com/my/resources/path/to/resource
        ``default:`` 'http://www.example.com'
        See also: :param:`resource_dir`

    :param str document_root: ``parameter`` :param:`document_root`
        ``parameter`` :samp:`The directory from which the server will serve files` (str)
        Example. Paths to resources are relative to the server host::

            url_prefix:         http://www.example.com
            url to resource:    http://www.example.com/path/to/resource
            document_root:               /var/www/html/
            path on server:              /var/www/html/path/to/resource
        Example. Paths to resources are relative to some directory on the server::

            url_prefix:         http://www.example.com/my/resources
            url to resource:    http://www.example.com/my/resources/path/to/resource
            document_root:               /var/www/html/my/resources
            path on server:              /var/www/html/my/resources/path/to/resource
        ``default:`` '/var/www/html/'
    :param Union[Strategy, int, str] strategy: ``parameter`` :param:`strategy`
        ``parameter`` :samp:`Strategy for ResourceSync publishing` (str | int | :class:`~resourcesync.parameters.enum.Strategy`)

        The `strategy` determines what will be done by :class:`~resourcesync.resourcesync.ResourceSync` upon execution.
        At the moment valid values for `strategy` are:

        - ``0`` :attr:`~resourcesync.parameters.enum.Strategy.resourcelist` - new resourcelist: create new resourcelist(s)
        - ``1`` :attr:`~rspub.core.rs_enum.Strategy.new_changelist` - new changelist: create a new changelist on every execution
        - ``2`` :attr:`~rspub.core.rs_enum.Strategy.inc_changelist` - incremental changelist: add changes to an existing changelist

        If strategies new resourcelist or incremental changelist are chosen and there is no previous resourcelist
        found in the metadata directory the strategy :attr:`~rspub.core.rs_enum.Strategy.resourcelist` will be executed.
        ``default:`` :attr:`rspub.core.rs_enum.Strategy.resourcelist`
    :param str generator: ``parameter`` :param:`generator`
        ``parameter`` :samp: `Generator for ResourceSync publishing` (str)

        The `generator` is the class name of the pluggable component responsible for providing metadata items
          (the data in the element url of an urlset).
    :param str plugin_dir: ``parameter`` :param:`plugin_dir`
        ``parameter`` :samp:`Directory where plugins can be found` (str)

        The given value should point to an existing directory. A relative path will be made absolute, calculated
        from the current working directory (`os.getcwd()`).

        At the moment plugins for :class:`~rspub.pluggable.gate.ResourceGateBuilder` can be provided.
        ``default:`` **None**
        See also: :doc:`rspub.util.gates <rspub.util.gates>`
    :param str history_dir: ``parameter`` :param:`history_dir`
        ``parameter`` :samp:`Directory for storing reports on executed synchronisations` (str)

        Currently not in use.
    :param int max_items_in_list: ``parameter`` :param:`max_items_in_list`
        ``parameter`` :samp:`The maximum amount of records in a sitemap` (int, 1 - 50000)

        The 'community defined' maximum amount of records in a sitemap document is 50000. If on execution
        the maximum amount is reached, new sitemaps of the same category will be created with the remaining
        records.

        ``default:`` 50000
    :param int zero_fill_filename: ``parameter`` :param:`zero_fill_filename`
        ``parameter`` :samp:`The amount of digits in a sitemap filename` (int, 1 - 10)

        Filenames of resourcelist, changelist etc. are numbered and are post-fixed with this number filled with
        zero's up to `zero_fill_filename`. Examples of filenames with `zero_fill_filename` set at 4::

            changelist_0002.xml
            changelist_0003.xml

        ``default:`` 4
    :param bool is_saving_pretty_xml: ``parameter`` :param:`is_saving_pretty_xml`
        ``parameter`` :samp:`Determines appearance of sitemap xml` (bool)

        If no humans need to read or inspect sitemaps there is no need for linebreaks etc.

        ``default:`` **True**, with linebreaks
    :param bool is_saving_sitemaps: ``parameter`` :param:`is_saving_sitemaps`
        ``parameter`` :samp:`Determines if sitemaps will be written to disk` (bool)

        An execution can be a dry-run. With this parameter set to **False** sitemaps will be generated,
        but not written to disk.

        ``default:`` **True**, write sitemaps to disk
    :param bool has_wellknown_at_root: ``parameter`` :param:`has_wellknown_at_root`
        ``parameter`` :samp:`Where is the description document {.well-known/resourcesync} on the server` (bool)

        The description document is the main entry point for third parties trying to discover resources at
        a source. Capability lists point toward this document in their `rel:up` attribute. If for some
        reason the `.well-known/resourcesync` cannot be at the root of the server the `rel:up` link in
        capability lists will be made to be pointing at `.well-known/resourcesync` relative to
        :func:`abs_metadata_dir`.

        ``default:`` **True**, the `.well-known/resourcesync` is at the root of the server
    
    :raises: :exc:`ValueError` if a parameter is not valid or if the configuration with the given `config_name` is not found
"""

    _instance = None
    _configuration_filename = CFG_FILENAME

    def __init__(self, **kwargs):
        self.__dict__["param_dict"] = {}
        self.param_dict = {}
        self.__init_param("config_name", default=None, convert=None, validator=None,
                          metadata={"type": ["str"]}, **kwargs)
        self.__init_param("resource_dir", default="~", convert=ParameterUtils.get_resource_dir,
                          validator=None, metadata=None, **kwargs)
        self.__init_param("metadata_dir", default="metadata", convert=ParameterUtils.get_metadata_dir,
                          validator=None, metadata=None, **kwargs)
        self.__init_param("description_dir", default=None, convert=ParameterUtils.get_description_dir,
                          validator=None, metadata=None, **kwargs)
        self.__init_param("url_prefix", default="http://www.example.com", convert=ParameterUtils.get_url_prefix,
                          validator=None, metadata=None, **kwargs)
        self.__init_param("document_root", default="/var/www/html", convert=ParameterUtils.get_document_root,
                          validator=None, metadata=None, **kwargs)
        self.__init_param("strategy", default=Strategy.resourcelist.name, convert=ParameterUtils.get_strategy,
                          validator=None, metadata=None, **kwargs)
        self.__init_param("generator", default=None, convert=None, validator=None,
                          metadata={"type": ["str"]}, **kwargs)
        self.__init_param("plugin_dir", default=None, convert=ParameterUtils.get_plugin_dir,
                          validator=None, metadata=None, **kwargs)
        self.__init_param("history_dir", default=None, convert=ParameterUtils.get_history_dir,
                          validator=None, metadata=None, **kwargs)
        self.__init_param("max_items_in_list", default=50000, convert=None,
                          validator=ParameterUtils.assert_max_items_in_list,
                          metadata={"type": ["int"]}, **kwargs)
        self.__init_param("zero_fill_filename", default=4, convert=None,
                          validator=ParameterUtils.assert_zero_fill_filename_range,
                          metadata={"type": ["int"]}, **kwargs)
        self.__init_param("is_saving_pretty_xml", default=True, convert=None,
                          validator=None, metadata={"type": ["bool"]}, **kwargs)
        self.__init_param("is_saving_sitemaps", default=True, convert=None,
                          validator=None, metadata={"type": ["bool"]}, **kwargs)
        self.__init_param("has_wellknown_at_root", default=True, convert=None,
                          validator=None, metadata={"type": ["bool"]}, **kwargs)
        for key, value in kwargs.items():
            if key not in self.param_dict:
                self.__init_param(key, default=value, convert=None, validator=None, metadata=None, **kwargs)

        self.__update_from_config_file()

    def __init_param(self, name, default=None, convert=None, validator=None, metadata=None,
                     **kwargs):

        self.param_dict[name] = {
            "default": kwargs.get(name) if kwargs.get(name) is not None else default,
            "convert": convert,
            "validator": validator,
            "metadata": metadata
        }
        logging.debug("param_dict set for %s\n%s" % (name, self.param_dict.get(name)))
        setattr(self, name, self.param_dict[name].get("default"))

    def __update_from_config_file(self):
        if not self.config_name:
            return

        Parameters.__get__logger().debug("Updating config from file.")
        for field, param in self.param_dict.items():
            value = None
            if param.get("metadata") and "int" in param.get("metadata").get("type"):
                try:
                    value = self.parser.getint(SECTION_CORE, field, fallback=param.get("default"))
                except ValueError:
                    pass
            elif param.get("metadata") and "bool" in param.get("metadata").get("type"):
                try:
                    value = self.parser.getboolean(SECTION_CORE, field, fallback=param.get("default"))
                except ValueError:
                    pass
            if not value:
                value = self.parser.get(SECTION_CORE, field, fallback=param.get("default"))
            fvalue = self.__convert_and_validate(param, value)
            self.__dict__[field] = fvalue

    def __convert_and_validate(self, param, value):
        if param.get("convert") is not None:
            fvalue = param.get("convert")(value)
        else:
            fvalue = value
        if param.get("validator") is not None:
            param.get("validator")(fvalue)
        elif param.get("metadata") and param.get("metadata").get("type"):
            if "bool" in param.get("metadata").get("type"):
                if not isinstance(fvalue, bool):
                    raise TypeError
            elif "int" in param.get("metadata").get("type"):
                if not isinstance(fvalue, int):
                    raise TypeError
            elif "str" in param.get("metadata").get("type") and fvalue:
                if not isinstance(fvalue, str):
                    raise TypeError
        return fvalue

    def __setattr__(self, key, value):
        if not self.__dict__.get("param_dict"):
            logging.debug("param_dict not set")
            return
        Parameters.__get__logger().debug("Setting attribute %s" % key)
        field = self.param_dict.get(key)

        if field:
            fvalue = self.__convert_and_validate(field, value)
            self.__dict__[key] = fvalue
            Parameters.__get__logger().debug("Setting attribute %s with value %s" % (key, fvalue))
        else:
            self.__dict__[key] = value
            Parameters.__get__logger().debug("Setting attribute %s with value %s" % (key, value))

    @staticmethod
    def __get__logger():
        logger = logging.getLogger(__name__)
        return logger

    @staticmethod
    def _set_configuration_filename(cfg_filename):
        Parameters.__get__logger().debug("Setting configuration filename to %s", cfg_filename)
        Parameters._configuration_filename = cfg_filename

    @staticmethod
    def _get_configuration_filename():
        if not Parameters._configuration_filename:
            Parameters._set_configuration_filename(CFG_FILENAME)

        return Parameters._configuration_filename

    @staticmethod
    def reset():
        Parameters._instance = None
        Parameters.__get__logger().debug("Configuration was reset.")

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
        Parameters.__get__logger().info("Configuration directory: %s", c_path)
        return c_path

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            Parameters.__get__logger().debug("Creating Configuration._instance")
            cls._instance = super(Parameters, cls).__new__(cls, *args)
            cls.config_path = cls._get_config_path()
            cls.config_file = os.path.join(cls.config_path, Parameters._get_configuration_filename())
            cls.parser = ConfigParser()
            if os.path.exists(cls.config_file):
                cls.parser.read(cls.config_file, encoding="utf-8")
        return cls._instance

    @staticmethod
    def reset():
        Parameters._instance = None
        Parameters.__get__logger().debug("Configuration was reset.")

    def abs_metadata_dir(self) -> str:
        """
        ``derived`` :samp:`The absolute path to metadata directory`

        :return: absolute path to metadata directory
        """
        return os.path.join(self.resource_dir, self.metadata_dir)

    def abs_metadata_path(self, filename):
        """
        ``derived`` :samp:`The absolute path to file in the metadata directory`

        :param str filename: the filename to position relative to the :func:`abs_metadata_dir`
        :return: absolute path to file in the metadata directory
        """
        return os.path.join(self.abs_metadata_dir(), filename)

    def abs_description_path(self):
        """
        ``derived`` :samp:`The absolute path to (the local copy of) the file {.well-known/resourcesync}`

        :return: absolute path to (the local copy of) the file ``.well-known/resourcesync``
        """
        desc_dir = self.description_dir
        if desc_dir is None or desc_dir == "":
            desc_dir = self.abs_metadata_dir()
        return os.path.join(desc_dir, WELL_KNOWN_PATH)

    def server_root(self):
        """
        ``derived`` :samp:`The server root as derived from {url_prefix}`

        :return: server root
        """
        r = urllib.parse.urlsplit(self.url_prefix)
        return urllib.parse.urlunsplit([r[0], r[1], "", "", ""])

    def description_url(self):
        """
        ``derived`` :samp:`The current description url`

        The current description url either points to ``{server root}/.well-known/resourcesync``
        or to a file in the metadata directory.

        :return: current description url

        See also: :func:`has_wellknown_at_root`
        """
        if self.has_wellknown_at_root:
            r = urllib.parse.urlsplit(self.url_prefix)
            return urllib.parse.urlunsplit([r[0], r[1], WELL_KNOWN_URL, "", ""])
        else:
            path = self.abs_metadata_path(WELL_KNOWN_URL)
            rel_path = os.path.relpath(path, self.resource_dir)
            return self.url_prefix + defaults.sanitize_url_path(rel_path)

    def capabilitylist_url(self) -> str:
        """
        ``derived`` :samp:`The current capabilitylist url`

        The current capabilitylist url points to 'capabilitylist.xml' in the metadata directory.

        :return: current capabilitylist url
        """
        path = self.abs_metadata_path("capabilitylist.xml")
        rel_path = os.path.relpath(path, self.resource_dir)
        return self.url_prefix + defaults.sanitize_url_path(rel_path)

    def uri_from_path(self, path):
        """
        ``derived`` :samp:`Calculate the url of a path relative to {resource_dir}`

        :param str path: the path to calculate the url from
        :return: the url of the path relative to ``resource_dir``
        """
        rel_path = os.path.relpath(path, self.resource_dir)
        return self.url_prefix + defaults.sanitize_url_path(rel_path)

    def abs_history_dir(self):
        """
        ``derived`` :samp:`The absolute path to directory for reports on synchronizations`

        Currently not in use.

        :return: absolute path to directory for reports
        """
        if self.history_dir:
            return os.path.join(self.abs_metadata_dir(), self.history_dir)
        else:
            return None

    def example_filename(self, ordinal):
        if self.strategy == Strategy.resourcelist:
            return "resourcelist_" + str(ordinal).zfill(self.zero_fill_filename) + ".xml"
        else:
            return "changelist_" + str(ordinal).zfill(self.zero_fill_filename) + ".xml"

    def describe(self, as_string=False, fill=23):
        """
        ``function`` :samp:`List parameters and derived values`

        List parameters, values and derived values as a list of tuples. Each tuple contains:

        ===  =====  ========================================================
        n    field  contents
        ===  =====  ========================================================
        0    bool   **True** for ``parameter``, **False** for derived value
        1    name   The name of the parameter or derived value
        2    value  The value of the parameter or derived value
        3..  ...    Anything else
        ===  =====  ========================================================

        :param as_string: return contents as a printable string
        :param fill: if as_string: fill column 'name' with `fill` spaces
        :return: list[list] or str
        """
        tuples = [
            [False, "configuration_name", self.configuration_name()],
            [True, "resource_dir", self.resource_dir],
            [True, "metadata_dir", self.metadata_dir],
            [False, "abs_metadata_dir", self.abs_metadata_dir()],
            [True, "description_dir", self.description_dir],
            [False, "abs_description_path", self.abs_description_path()],
            [True, "url_prefix", self.url_prefix],
            [True, "document_root", self.document_root],
            [True, "has_wellknown_at_root", self.has_wellknown_at_root],
            [False, "description_url", self.description_url()],
            [False, "capabilitylist_url", self.capabilitylist_url()],
            [True, "strategy", self.strategy, self.strategy.describe()],
            [True, "generator", self.generator, self.generator.__class__],
            [True, "plugin_dir", self.plugin_dir],
            [True, "max_items_in_list", self.max_items_in_list],
            [True, "zero_fill_filename", self.zero_fill_filename],
            [False, "example_filename", self.example_filename(42)],
            [True, "is_saving_pretty_xml", self.is_saving_pretty_xml],
            [True, "is_saving_sitemaps", self.is_saving_sitemaps],
            [False, "last_execution", self.last_execution]
        ]
        if as_string:
            f = "{:" + str(fill) + "s}"
            s = ""
            for t in tuples:
                s += " - " if t[0] else " + "
                s += f.format(t[1])
                s += str(t[2])
                for extra in t[3:]:
                    s += " | "
                    s += str(extra)
                s += "\n"
            return s
        else:
            return tuples

    def persist(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            self.parser.write(f)
        Parameters.__get__logger().debug("Persisted %s", self.config_file)

    def save_configuration(self, on_disk=True):
        """
        ``function`` :samp:`Save current configuration`

        Save the current values of parameters to configuration. If `on_disk` is **True** (the default)
        persist the configuration to disk under the current configuration name.

        :param on_disk: **True** if configuration should be saved to disk, **False** otherwise
        """

        if not self.parser.has_section(SECTION_CORE):
            self.parser.add_section(SECTION_CORE)
        for f, p in self.param_dict.items():
            if self.__dict__.get(f) is None:
                self.parser.remove_option(SECTION_CORE, f)
            else:
                val = self.__dict__.get(f)
                if isinstance(val, Strategy):
                    val = val.name
                elif type(val) is not str:
                    val = str(val)
                self.parser.set(SECTION_CORE, f, val)

        if on_disk:
            self.persist()

