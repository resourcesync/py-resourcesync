from resourcesync.generators.elastic.model.link import Link
from resourcesync.generators.elastic.model.location import Location


class ResourceDoc(object):
    def __init__(self, resync_id=None, resource_set=None,
                 location: Location=None, length: int=None, md5: str=None,
                 mime: str=None, lastmod: str=None, ln: [Link]=None, timestamp: str=None):
        self._resync_id = resync_id
        self._resource_set = resource_set
        self._location = location
        self._length = length
        self._md5 = md5
        self._mime = mime
        self._lastmod = lastmod
        self._ln = ln if ln is not None else []
        self._timestamp = timestamp

    @property
    def resync_id(self):
        return self._resync_id

    @property
    def resource_set(self):
        return self._resource_set

    @property
    def location(self):
        return self._location

    @property
    def length(self):
        return self._length

    @property
    def md5(self):
        return self._md5

    @property
    def mime(self):
        return self._mime

    @property
    def lastmod(self):
        return self._lastmod

    @property
    def ln(self):
        return self._ln

    @ln.setter
    def ln(self, ln):
        self._ln = ln

    @property
    def timestamp(self):
        return self._timestamp

    @location.setter
    def location(self, location: Location):
        self._location = location

    @staticmethod
    def as_resource_doc(dct):
        return ResourceDoc(resync_id=dct['resync_id'],
                           resource_set=dct['resource_set'],
                           location=Location.as_location(dct=dct['location']),
                           length=dct['length'],
                           md5=dct['md5'],
                           mime=dct['mime'],
                           lastmod=dct['lastmod'],
                           ln=[Link.as_link(dct=link) for link in dct['ln']],
                           timestamp=dct['timestamp'])

    def to_dict(self):
        return {
            'resync_id': self.resync_id,
            'resource_set': self.resource_set,
            'location': self.location.to_dict(),
            'length': self.length,
            'md5': self.md5,
            'mime': self.mime,
            'lastmod': self.lastmod,
            'ln': [link.to_dict() for link in self.ln],
            'timestamp': self.timestamp
        }
