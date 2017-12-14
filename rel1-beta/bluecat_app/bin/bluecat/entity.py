from suds import WebFault

from api_exception import api_exception
from util import *
from version import version

from wrappers.generic_setters import *

class entity(object):
    """Instantiate an entity. Entities are hashable and comparable with the = operator.

    :param api: API instance used by the entity to communicate with BAM.
    :param soap_entity: the SOAP (suds) entity returned by the BAM API.
    :param soap_client: the suds client instance.

    """

    def __init__(self, api, soap_entity, soap_client, ver=''):
        self._api = api
        if not ver:
            self._version = api.get_version()
        else:
            self._version = version(ver)
        if (self._version >= '8.1.0'):
            self._none_parameter = ''
        else:
            self._none_parameter = None
        self._soap_entity = soap_entity
        self._soap_client = soap_client
        self._properties = {}
        self._immutable_properties = ['parentId', 'parentType']
        if 'properties' in self._soap_entity and self._soap_entity['properties'] is not None:
            self._properties = properties_to_map(self._soap_entity['properties'])

    Entity = 'Entity'
    Configuration = 'Configuration'
    View = 'View'
    Zone = 'Zone'
    InternalRootZone = 'InternalRootZone'
    ZoneTemplate = 'ZoneTemplate'
    EnumZone = 'EnumZone'
    EnumNumber = 'EnumNumber'
    RPZone = 'RPZone'
    HostRecord = 'HostRecord'
    AliasRecord = 'AliasRecord'
    MXRecord = 'MXRecord'
    TXTRecord = 'TXTRecord'
    SRVRecord = 'SRVRecord'
    GenericRecord = 'GenericRecord'
    HINFORecord = 'HINFORecord'
    NAPTRRecord = 'NAPTRRecord'
    RecordWithLink = 'RecordWithLink'
    ExternalHostRecord = 'ExternalHostRecord'
    StartOfAuthority = 'StartOfAuthority'
    IP4Block = 'IP4Block'
    IP4Network = 'IP4Network'
    IP6Block = 'IP6Block'
    IP6Network = 'IP6Network'
    IP4NetworkTemplate = 'IP4NetworkTemplate'
    DHCP4Range = 'DHCP4Range'
    IP4Address = 'IP4Address'
    IP6Address = 'IP6Address'
    InterfaceID = 'InterfaceID'
    MACPool = 'MACPool'
    DenyMACPool = 'DenyMACPool'
    MACAddress = 'MACAddress'
    TagGroup = 'TagGroup'
    Tag = 'Tag'
    User = 'User'
    UserGroup = 'UserGroup'
    Server = 'Server'
    NetworkServerInterface = 'NetworkServerInterface'
    PublishedServerInterface = 'PublishedServerInterface'
    NetworkInterface = 'NetworkInterface'
    VirtualInterface = 'VirtualInterface'
    LDAP = 'LDAP'
    Kerberos = 'Kerberos'
    Radius = 'Radius'
    TFTPGroup = 'TFTPGroup'
    TFTPFolder = 'TFTPFolder'
    TFTPFile = 'TFTPFile'
    TFTPDeploymentRole = 'TFTPDeploymentRole'
    DeploymentRole = 'DNSDeploymentRole'
    DHCPDeploymentRole = 'DHCPDeploymentRole'
    DNSOption = 'DNSOption'
    DHCPV4ClientOption = 'DHCPV4ClientOption'
    DHCPServiceOption = 'DHCPServiceOption'
    DHCPV6ClientOption = 'DHCPV6ClientOption'
    DHCPV6ServiceOption = 'DHCPV6ServiceOption'
    VendorProfile = 'VendorProfile'
    VendorOptionDef = 'VendorOptionDef'
    VendorClientOption = 'VendorClientOption'
    CustomOptionDef = 'CustomOptionDef'
    DHCPMatchClass = 'DHCPMatchClass'
    DHCPSubClass = 'DHCPSubClass'
    Device = 'Device'
    DeviceType = 'DeviceType'
    DeviceSubtype = 'DeviceSubtype'
    DeploymentScheduler = 'DeploymentScheduler'
    IP4ReconciliationPolicy = 'IP4ReconciliationPolicy'
    DNSSECSigningPolicy = 'DNSSECSigningPolicy'
    IP4IPGroup = 'IP4IPGroup'
    ResponsePolicy = 'ResponsePolicy'
    KerberosRealm = 'KerberosRealm'
    DHCPRawOption = 'DHCPRawOption'
    DHCPV6RawOption = 'DHCPV6RawOption'
    DNSRawOption = 'DNSRawOption'
    DHCP6Range = 'DHCP6Range'
    ACL = 'ACL'
    TSIGKey = 'TSIGKey'

    def __hash__(self):
        return hash(self.get_id())

    def __eq__(self, other):
        return self.get_id() == other.get_id()

    def get_url(self):
        return self._api.get_url()

    def get_id(self):
        """Get the BAM ID of an entity.
        """
        return self._soap_entity['id']

    def is_null(self):
        """Is this the null entity? (ID == 0).
        """
        return 'id' not in self._soap_entity or self._soap_entity['id'] == 0

    def get_name(self):
        """Get the BAM name of the entity.
        """
        if 'name' in self._soap_entity:
            return self._soap_entity['name']
        else:
            return None

    def get_type(self):
        """Get the BAM type of the entity.
        """
        return self._soap_entity['type']

    def get_properties(self):
        """Get the properties of the entity in the form of a dictionary containing one entry per property.
        """
        return self._properties

    def get_property(self, name):
        """Get a single named property for the entity or None if not defined.
        """
        if name in self._properties:
            return self._properties[name]
        else:
            return None

    def get_parent(self):
        """Get the parent entity or None if the entity is at the top of the hierarchy.
        """
        try:
            res = self._api.instantiate_entity(self._soap_client.service.getParent(self.get_id()), self._soap_client)
            return None if res.get_id() == 0 else res
        except WebFault as e:
            raise api_exception(e.message)

    def get_parent_of_type(self, type):
        """Walk up the entity hierarchy and return the first parent entity of the given type or, if none was found, None
        """
        parent = self
        count = 0
        while count < 100:
            parent = parent.get_parent()
            if parent.is_null():
                raise api_exception('No parent of type %s found.' % type)
            if parent.get_type() == type:
                try:
                    return self._api.instantiate_entity(self._soap_client.service.getEntityById(parent.get_id()),
                                                        self._soap_client)
                except WebFault as e:
                    raise api_exception(e.message)
            if count >= 100:
                raise api_exception('API failure, no parent of type %s found.' % type)

    def get_children_of_type(self, type, max_results=500):
        """Get all the immediate children of an entity of the given type.
        """
        try:
            res = []
            s = self._soap_client.service.getEntities(self.get_id(), type, 0, max_results)
            if not has_response(s):
                return res
            else:
                for dr in s.item:
                    res.append(self._api.instantiate_entity(dr, self._soap_client))
            return res
        except WebFault as e:
            raise api_exception(e.message)

    def get_linked_entities(self, type, max_results=500):
        """Get all the linked entities of a given type
        """
        try:
            res = []
            s = self._soap_client.service.getLinkedEntities(self.get_id(), type, 0, max_results)
            if not has_response(s):
                return res
            else:
                for dr in s.item:
                    res.append(self._api.instantiate_entity(dr, self._soap_client))
            return res
        except WebFault as e:
            raise api_exception(e.message)

    def get_child_by_name(self, name, type):
        """Get a specific named immediate child entity of a given type.
        """
        try:
            res = self._soap_client.service.getEntityByName(self.get_id(), name, type)
            if not has_response(res):
                return None
            else:
                return self._api.instantiate_entity(res, self._soap_client)
        except WebFault as e:
            raise api_exception(e.message)

    def set_property(self, name, value):
        """Set a property value. The change is not persisted until update() is called.
        """
        self._properties[name] = value

    def update(self):
        """Persist any changes to the entity to the BAM database.
        """
        s = ''
        for k, v in self._properties.items():
            if k not in self._immutable_properties:
                s += k + '=' + v + '|'
        self._soap_entity['properties'] = s
        try:
            self._soap_client.service.update(self._soap_entity)
        except WebFault as e:
            raise api_exception(e.message)

    def delete(self):
        """Delete the entity from the BAM database.
        """
        try:
            delete_entity(self._soap_client, self.get_id(), self._version)
        except WebFault as e:
            raise api_exception(e.message)

    def dump(self):
        """Dump out details of the entity to stdout. Useful for debug.
        """
        print self._soap_entity

    def get_deployment_roles(self, types=[]):
        """Get deployment roles for the entity.

        :param types: An optional list of deployment role types (documented in the deployment_role class). If the list is empty all types are returned.

        """
        try:
            res = []
            s = self._soap_client.service.getDeploymentRoles(self.get_id())
            if has_response(s):
                for dr in self._soap_client.service.getDeploymentRoles(self.get_id()).item:
                    if len(types) > 0 and dr['type'] in types:
                        res.append(self._api.instantiate_entity(dr, self._soap_client))
            return res
        except WebFault as e:
            raise api_exception(e.message)
