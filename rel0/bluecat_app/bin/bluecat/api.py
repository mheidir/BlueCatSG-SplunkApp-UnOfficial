"""
This is the main entry point for the API. The most common usage pattern is to create a 
connection via instantitation, login with the login method and then to
retrieve a configuration object via get_configuration or get_configurations.
"""

from suds import WebFault
from suds.client import Client

from configuration import configuration
from deployment_role import deployment_role
from entity import entity
from enum_zone import enum_zone, enum_number
from host_record import host_record
from ip4_address import ip4_address
from ip4_block import ip4_block
from ip4_network import ip4_network
from bdds_server import server
from resource_record import alias_record, mx_record, text_record, host_info_record, external_host_record, srv_record, naptr_record, generic_record
from sslcontext import create_ssl_context, HTTPSTransport
from user import user
from util import *
from view import view
from zone import zone
from version import version

from wrappers import generic_getters as generic_getter
from wrappers import generic_setters as generic_setter
from wrappers import user_api
from wrappers.api_entity import api_entity


class api(object):
    """Create a connection to the BAM API.

    :param url: URL of the BAM API (can be http or https).
    :param sslverify: Whether or not to verify the certificate installed on the BAM. Will generally be false for self signed certificates.
    :param ca_file: Name of the file listing CA's for use in verification.
    :param ca_path: CA path used for verification.
    """

    def __init__(self, url, sslverify=False, ca_file=None, ca_path=None):
        self._url = url
        if url[0:5] == 'https':
            kwargs = {}
            kwargs['transport'] = HTTPSTransport(create_ssl_context(sslverify, ca_file, ca_path))
            self._soap_client = Client(url, **kwargs)
        else:
            self._soap_client = Client(url)
        self._version = ''

    def get_url(self):
        """Get the url of the application.
        """
        return self._url

    def print_bam_soap_methods(self):
        """Print details of the various BAM SOAP API methods to stdout. Useful for debugging purposes.
        """
        print self._soap_client

    def login(self, username, password):
        """Login to the BAM API using the supplied username and password. The user must be set up with API access via
        the BAM GUI. All normal permissioning applies.

        :param username: BAM username.
        :param password: BAM password.
        """
        try:
            self._soap_client.service.login(username, password)
            self._get_system_version()
        except WebFault as e:
            raise api_exception(e.message)

    def logout(self):
        """Logout from the BAM API.
        """
        try:
            self._soap_client.service.logout()
            self._version = ''
        except WebFault as e:
            raise api_exception(e.message)

    def get_configurations(self, max_results=100):
        """Get up to max_results configurations.

        :param max_results: Maximum number of configurations to be returned.
        :return: List of :py:mod:`configuration` objects.
        """
        try:
            soap_entities = self._soap_client.service.getEntities(0, entity.Configuration, 0, max_results)
            if has_response(soap_entities):
                return [configuration(self, e, self._soap_client) for e in soap_entities.item]
            else:
                return []
        except WebFault as e:
            raise api_exception(e.message)

    def get_configuration(self, name):
        """Get a named configuration.

        :param name: Name of the BAM configuration.
        :return: :py:mod:`configuration` object of the named configuration
        """
        try:
            soap_entities = self._soap_client.service.getEntitiesByName(0, name, entity.Configuration, 0, 10)
        except WebFault as e:
            raise api_exception(e.message)
        if not hasattr(soap_entities, 'item') or len(soap_entities.item) == 0:
            raise api_exception('No configuration named %s found' % name)
        elif len(soap_entities.item) == 1:
            return configuration(self, soap_entities.item[0], self._soap_client)
        else:
            raise api_exception('More than 1 configuration called %s found' % name)

    def get_user(self, username):
        """Get a named user.

        :param username: Username of the BAM user.
        :return: :py:mod:`user` object for the username
        """
        try:
            e = self._soap_client.service.getEntityByName(0, username, entity.User)
        except WebFault as e:
            raise api_exception(e.message)
        if not has_response(e):
            raise api_exception('No user named %s found' % username)
        else:
            return user(self, e, self._soap_client)

    def get_entity_by_id(self, entity_id):
        """Get an entity by its ID. The returned object is of the correct class or, if none is defined, is an entity instance.

        :param entity_id: BAM entity ID (note that these are unique across all configurations).
        :return:
        """
        try:
            e = self._soap_client.service.getEntityById(entity_id)
        except WebFault as e:
            raise api_exception(e.message)
        if not has_response(e):
            raise api_exception('No such entity exists.', entity_id)
        else:
            return self.instantiate_entity(e, self._soap_client)

    def get_system_info(self):
        """Get current system information in the form of a name/value pair dictionary.

        :return:
        """
        try:
            return properties_to_map(self._soap_client.service.getSystemInfo())
        except WebFault as e:
            raise api_exception(e.message)

    def _get_system_version(self):
        if self._version == '':
            try:
                self._version = version(self.get_system_info()['version'].split('-')[0])
            except WebFault as e:
                raise api_exception(e.message)

    def get_version(self):
        """Get current system version from the system information as <major version>.<minor version>.<patch>

        :return: Version string. eg. '8.0.0'
        """
        if self._version == '':
            self._get_system_version()
        return self._version

    def instantiate_entity(self, e, soap_client):
        """Instantiate an appropriate python class given an entity returned from a SOAP call.

        :param e: SOAP entity.
        :param soap_client: BAM SOAP client connection for the entity instance to use when accessing the API.
        :return: A type specific instance object of the SOAP entity or generic entity object. None if there is no type.
        """
        if 'type' in e:
            t = e['type']
            if t == entity.Configuration:
                return configuration(self, e, soap_client)
            elif t == entity.User:
                return user(self, e, soap_client)
            elif t == entity.Zone:
                return zone(self, e, soap_client)
            elif t == entity.View:
                return view(self, e, soap_client)
            elif t == entity.IP4Block:
                return ip4_block(self, e, soap_client)
            elif t == entity.IP4Network:
                return ip4_network(self, e, soap_client)
            elif t == entity.HostRecord:
                return host_record(self, e, soap_client)
            elif t == entity.AliasRecord:
                return alias_record(self, e, soap_client)
            elif t == entity.MXRecord:
                return mx_record(self, e, soap_client)
            elif t == entity.TXTRecord:
                return text_record(self, e, soap_client)
            elif t == entity.HINFORecord:
                return host_info_record(self, e, soap_client)
            elif t == entity.SRVRecord:
                return srv_record(self, e, soap_client)
            elif t == entity.NAPTRRecord:
                return naptr_record(self, e, soap_client)
            elif t == entity.ExternalHostRecord:
                return external_host_record(self, e, soap_client)
            elif t == entity.GenericRecord:
                return generic_record(self, e, soap_client)
            elif t == entity.EnumZone:
                return enum_zone(self, e, soap_client)
            elif t== entity.EnumNumber:
                return enum_number(self, e, soap_client)
            elif t in deployment_role.roles:
                return deployment_role(self, e, soap_client)
            elif t == entity.IP4Address:
                return ip4_address(self, e, soap_client)
            elif t == entity.Server:
                return server(self, e, soap_client)
            else:
                return entity(self, e, soap_client)
        else:
            return None

    def get_by_object_types(self, pattern, types, max_results=100):
        """Get a list of objects based on a search pattern and a list of object types.

        :param pattern: search pattern (will match any of the various properties of a BAM entity).
        :param types: list of BAM entity types (e.g. [entity.View, entity.Configuration])
        :param max_results: maximum number of entities to be returned.
        :return: List of objects
        """
        res = []
        for start in range(0, max_results, 100):
            try:
                objs = self._soap_client.service.searchByObjectTypes(pattern, ','.join(types), start, 100)
            except WebFault as e:
                raise api_exception(e.message)
            if len(objs) > 0:
                res += [self.instantiate_entity(e, self._soap_client) for e in objs.item]
        return res

    def create_configuration(self, name):
        """Creates a configuration in the BAM with the given name"""

        try:
            config_entity = api_entity(self._soap_client)
            config_entity.name = name
            config_entity.type = entity.Configuration
            result = generic_setter.add_entity(self._soap_client, 0, config_entity.get_entity(), version=self.get_version())
            if result == 0:
                raise api_exception("Failed to create configuration.")
            return self.get_entity_by_id(result)
        except WebFault as e:
            raise api_exception(e.message)

    def delete_configuration(self, name='', id=0):
        """
        Delete a configuration

        :param name:
        :param id:
        """
        try:
            if id:
                return generic_setter.delete_entity(self._soap_client, id)
            elif name:
                config = self.get_configuration(name)
                return generic_setter.delete_entity(self._soap_client, config.get_id(), version=self.get_version())
            raise api_exception("Did not give proper configuration id or name!")
        except WebFault as e:
            raise api_exception(e.message)

    def add_user(self, username, password, email='e@e', user_access_type='API', properties={}):
        """
        Add a user to BAM, options are listed in the options variable.

        :param username:
        :param password:
        :param properties:
        :param user_type:
        :param email:
        :param user_access_type:
        :return: :py:mod:`user` object of the added user
        """
        options = ['authenticator', 'securityPrivilege', 'historyPrivilege', 'email', 'phoneNumber', 'userType', 'userAccessType']
        property_string = ''
        try:
            if username and password:
                property_string = parse_properties(properties)
                if 'email' not in properties or 'email' not in property_string:
                    property_string += 'email=%s|' % email
                if 'userAccessType' not in properties or 'userAccessType' not in property_string:
                    property_string += 'userAccessType=%s|' % user_access_type
                return self.get_entity_by_id(user_api.add_user(self._soap_client, username, password, property_string, self.get_version()))
            else:
                raise api_exception("Username or password not given!")
        except WebFault as e:
            raise api_exception(e.message)

    def add_group(self, name, properties=''):
        """
        Add a user group

        :param name:
        :param properties:
        :return:
        """
        try:
            return self.get_entity_by_id(user_api.add_user_group(self._soap_client, name, version=self.get_version()))
        except WebFault as e:
            raise api_exception(e.message)

    def get_group(self, group_name):
        try:
            e = generic_getter.get_entity_by_name(self._soap_client, 0, group_name, 'UserGroup', version=self.get_version())
        except WebFault as e:
            raise api_exception(e.message)
        if not has_response(e):
            raise api_exception('No user group named %s found' % group_name)
        else:
            return self.instantiate_entity(e, self._soap_client)

    def delete_user(self, name='', id=0):
        """
        Delete a user, can use either username or user_id to specify which user to delete

        :param username:
        :param user_id:
        """
        try:
            if id:
                generic_setter.delete_entity(self._soap_client, id, version=self.get_version())
            elif name:
                generic_setter.delete_entity(self._soap_client, self.get_user(name).get_id(), version=self.get_version())
            else:
                raise api_exception('No proper username or user id given!')
        except api_exception as e:
            raise e

    def delete_group(self, name='', id=0):
        """
        Delete a group, accepts either the group's name or id

        :param name:
        :param id:
        """
        try:
            if id:
                generic_setter.delete_entity(self._soap_client, id, version=self.get_version())
            elif name:
                generic_setter.delete_entity(self._soap_client, self.get_group(name).get_id(), version=self.get_version())
            else:
                raise api_exception('No proper name or group id given!')
        except api_exception as e:
            raise e
