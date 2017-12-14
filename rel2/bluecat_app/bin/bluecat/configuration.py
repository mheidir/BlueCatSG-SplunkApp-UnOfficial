from suds import WebFault

from entity import entity
from ip4_address import ip4_address
from ip6_address import ip6_address
from view import view
from util import *

"""
BAM configuration objects (aka entities). All entities are children of configurations with various of them being
directly beneath.
"""

class ip_space_configuration(entity):
    """Instantiate a ip space configuration.

        :param api: API instance used by the entity to communicate with BAM.
        :param soap_entity: the SOAP (suds) entity returned by the BAM API.
        :param soap_client: the suds client instance.

        """

    def __init__(self, api, soap_entity, soap_client):
        super(ip_space_configuration, self).__init__(api, soap_entity, soap_client)

    def add_ip4_block_by_cidr(self, cidr, properties=''):
        """Create a new ip4 child block using CIDR.

        :param cidr: the CIDR notation defining the block (for example, 10.10/16).
        :param properties: A string containing options.

        """
        try:
            properties = parse_properties(properties)
            return self._api.get_entity_by_id(
                self._soap_client.service.addIP4BlockByCIDR(self.get_id(), cidr, properties))
        except WebFault as e:
	    if "Duplicate" in e.message:
            	return self._api.get_entity_by_id(
                    self.get_child_by_name(cidr, entity.IP4Block))
	    
            raise api_exception(e.message)

    def add_ip4_block_by_range(self, start, end, properties=''):
        """Create a new ip4 child block by defining an address range.

        :param start: An IP address defining the lowest address or start of the block.
        :param end: An IP address defining the highest address or end of the block.
        :param properties: A string containing options.

        """
        try:
            properties = parse_properties(properties)
            return self._api.get_entity_by_id(
                self._soap_client.service.addIP4BlockByRange(self.get_id(), start, end, properties))
        except WebFault as e:
            raise api_exception(e.message)

    def get_ip4_blocks(self, max_results=500, start=0):
        """Get the IP4 blocks directly underneath the current configuration or block. Note that blocks for the nodes of a tree with networks
           being the leaves.

        :param max_results: the maximum number of views that will be returned.
        """
        try:
            return self.get_children_of_type(entity.IP4Block, max_results=max_results)
        except WebFault as e:
            raise api_exception(e.message)

    def get_ip4_address(self, address):
        """Get an IP4 address by name (e.g. '192.168.0.1'). These are direct children of configurations.

        :param address: the IP4 address string.
        """
        try:
            e = self._soap_client.service.getIP4Address(self.get_id(), address)
            if e == '':
                raise api_exception('IP4 address not found', address)
            else:
                return ip4_address(self._api, e, self._soap_client)
        except WebFault as e:
            raise api_exception(e.message)

    def get_ip6_address(self, address):
        """Get an IP6 address by name (e.g. 'FE80:0000:0000:0000:0202:B3FF:FE1E:8329'). These are direct children of configurations.

        :param address: the IP6 address string.
        """
        try:
            e = self._soap_client.service.getIP6Address(self.get_id(), address)
            if e == '':
                raise api_exception('IP6 address not found', address)
            else:
                return ip6_address(self._api, e, self._soap_client)
        except WebFault as e:
            raise api_exception(e.message)

class dns_configuration(entity):
    """Instantiate a dns configuration.

    :param api: API instance used by the entity to communicate with BAM.
    :param soap_entity: the SOAP (suds) entity returned by the BAM API.
    :param soap_client: the suds client instance.

    """

    def __init__(self, api, soap_entity, soap_client):
        super(dns_configuration, self).__init__(api, soap_entity, soap_client)

    def add_view(self, name, properties = ''):
        try:
            properties = parse_properties(properties)
            return self._api.get_entity_by_id(
                self._soap_client.service.addView(self.get_id(), name, properties))
        except WebFault as e:
            raise api_exception(e.message)

    def get_views(self, max_results=100):
        """Get a list of all child views (ref: split horizon DNS) of the configuration upto a maximum number.

        :param max_results: the maximum number of views that will be returned.
        """
        try:
            soap_entities = self._soap_client.service.getEntities(self.get_id(), entity.View, 0, max_results)
            if soap_entities.item == '':
                return []
            else:
                return [view(self._api, e, self._soap_client) for e in soap_entities.item]
        except WebFault as e:
            raise api_exception(e.message)

    def get_view(self, name):
        """Get a named view (ref: split horizon DNS) out of a configuration. An exception is raised if the
           view doesn't exist.
        """
        try:
            soap_entities = self._soap_client.service.getEntitiesByName(self.get_id(), name, entity.View, 0, 10)
        except WebFault as e:
            raise api_exception(e.message)
        if not hasattr(soap_entities, 'item') or len(soap_entities.item) == 0:
            raise api_exception('No view named %s found under configuration %s.' % (name, self.get_name()))
        elif len(soap_entities.item) == 1:
            return view(self._api, soap_entities.item[0], self._soap_client)
        else:
            raise api_exception('More than 1 view called %s found under configuration %s.' % (name, self.get_name()))

class server_configuration(entity):
    """Instantiate a dns configuration.

    :param api: API instance used by the entity to communicate with BAM.
    :param soap_entity: the SOAP (suds) entity returned by the BAM API.
    :param soap_client: the suds client instance.

    """

    def __init__(self, api, soap_entity, soap_client):
        super(server_configuration, self).__init__(api, soap_entity, soap_client)

    def get_servers(self):
        """Get a list of all the servers in a configuration.
        """
        return self.get_children_of_type('Server')

    def get_server(self, name):
        """Get a named server. Returns None if the server wasn't found.
        """
        return self.get_child_by_name(name, 'Server')

    def add_server(self, name, address, host_name, properties='password=bluecat|connected=true|',
                   profile='DNS_DHCP_SERVER_60'):
        try:
            properties = parse_properties(properties)
            return self._api.get_entity_by_id(
                self._soap_client.service.addServer(self.get_id(), name, address, host_name, profile, properties))
        except WebFault as e:
            raise api_exception(e.message)

class configuration(ip_space_configuration, dns_configuration, server_configuration):
    """Instantiate a configuration.

    :param api: API instance used by the entity to communicate with BAM.
    :param soap_entity: the SOAP (suds) entity returned by the BAM API.
    :param soap_client: the suds client instance.

    """

    def __init__(self, api, soap_entity, soap_client):
        super(configuration, self).__init__(api, soap_entity, soap_client)




