from bluecat.version import version as ver

class api_entity(object):
    def __init__(self, soap_client, id=0, name='', type='', properties='', version='8.1.0'):
        self._api_entity = soap_client.factory.create('APIEntity')
        self._api_entity.id = id
        self._api_entity.name = name
        self._api_entity.properties = properties
        self._api_entity.type = type
        self._version = ver(version)

    @property
    def id(self):
        return self._api_entity.id

    @id.setter
    def id(self, value):
        self._api_entity.id = value

    @id.deleter
    def id(self):
        self._api_entity.id = 0

    @property
    def name(self):
        return self._api_entity.name

    @name.setter
    def name(self, value):
        self._api_entity.name = value

    @name.deleter
    def name(self):
        self._api_entity.name = ''

    @property
    def properties(self):
        return self._api_entity.properties

    @properties.setter
    def properties(self, value):
        self._api_entity.properties = value

    @properties.deleter
    def properties(self):
        self._api_entity.properties = ''

    @property
    def type(self):
        return self._api_entity.type

    @type.setter
    def type(self, value):
        self._api_entity.type = value

    @type.deleter
    def type(self):
        self._api_entity.type = ''

    def get_entity(self):
        if self._api_entity.id == None:
            self._api_entity.id = 0
        if self._api_entity.name == None:
            self._api_entity.name = ''
        if self._api_entity.type == None:
            self._api_entity.type = ''
        if self._api_entity.properties == None:
            self._api_entity.properties = ''
        return self._api_entity