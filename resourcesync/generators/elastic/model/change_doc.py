from resourcesync.generators.elastic.model.location import Location


class ChangeDoc(object):

    def __init__(self, resource_set: str=None, location: Location=None,
                 lastmod: str=None, change: str=None, datetime: str=None, timestamp: str=None):
        self._resource_set = resource_set
        self._location = location
        self._lastmod = lastmod
        self._change = change
        self._datetime = datetime
        self._timestamp = timestamp

    @property
    def resource_set(self):
        return self._resource_set

    @property
    def location(self):
        return self._location

    @property
    def lastmod(self):
        return self._lastmod

    @property
    def change(self):
        return self._change

    @property
    def datetime(self):
        return self._datetime

    @property
    def timestamp(self):
        return self._timestamp

    @staticmethod
    def as_change_doc(dct: dict):
        return ChangeDoc(resource_set=dct.get('resource_set'),
                         location=Location.as_location(dct=dct.get('location')),
                         lastmod=dct.get('lastmod'),
                         change=dct.get('change'),
                         datetime=dct.get('datetime'),
                         timestamp=dct.get('timestamp'))

    def to_dict(self):
        return {
            'resource_set': self.resource_set,
            'change': self.change,
            'location': self.location.to_dict(),
            'lastmod': self.lastmod,
            'datetime': self.datetime,
            'timestamp': self.timestamp
        }

