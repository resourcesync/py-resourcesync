import os
from urllib.parse import urljoin

from resourcesync.utils import defaults


class Location(object):

    def __init__(self, value: str, loc_type: str):
        self._value = value
        self._loc_type = loc_type

    @property
    def value(self):
        return self._value

    @property
    def loc_type(self):
        return self._loc_type

    @value.setter
    def value(self, value):
        self._value = value

    @loc_type.setter
    def loc_type(self, loc_type):
        self._loc_type = loc_type

    def uri_from_path(self, param_url_prefix, param_resource_root_dir) -> str:
        uri = None
        if self.loc_type == 'url':
            uri = self.value
        elif self.loc_type == 'rel_path':
            uri = urljoin(param_url_prefix, defaults.sanitize_url_path(self.value))
        elif self.loc_type == 'abs_path':
            path = os.path.relpath(self.value, param_resource_root_dir)
            uri = param_url_prefix + defaults.sanitize_url_path(path)
        return uri

    @staticmethod
    def as_location(dct):
        return Location(value=dct['value'], loc_type=dct['type'])

    def to_dict(self) -> dict:
        return {
            'type': self.loc_type,
            'value': self.value
        }
