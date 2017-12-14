from entity import entity
from suds import WebFault
from api_exception import api_exception
from util import *
from configuration import ip_space_configuration

"""
IPv4 block obejcts. Blocks form the nodes of a tree with networks as the leaves.
"""


class ip4_block(ip_space_configuration):
    """Instantiate an ipv4_block.

    :param api: API instance used by the entity to communicate with BAM.
    :param soap_entity: the SOAP (suds) entity returned by the BAM API.
    :param soap_client: the suds client instance.

    """

    def __init__(self, api, soap_entity, soap_client):
        super(ip4_block, self).__init__(api, soap_entity, soap_client)

    """Get a list of the child networks of a block (if any).

    :max_results soap_client: the maximum number of networks to return.

    """

    def get_ip4_networks(self, max_results=500):
        return self.get_children_of_type(entity.IP4Network, max_results=max_results)

    """Adds an IPv4 network using CIDR notation.

    :cidr soap_client: the CIDR notation defining the network (for example, 10.10.10/24).
    :properties soap_client: A string containing options.

    """

    def add_ip4_network(self, cidr, properties=''):
        try:
            properties = parse_properties(properties)
            return self._api.get_entity_by_id(self._soap_client.service.addIP4Network(self.get_id(), cidr, properties))

        except WebFault as e:
            raise api_exception(e.message)

    """Creates an IPv4 or IPv6 block from a list of IPv4 or IPv6 blocks or networks. All blocks and networks must
    have the same parent but it does not need to be contiguous.

    :blockOrNetworkIDs soap_client: An array containing the object IDs of IPv4 or IPv6 blocks or networks.

    """

    def add_parent_block(self, block_or_network_ids):
        try:
            return self._api.get_entity_by_id(self._soap_client.service.addParentBlock(block_or_network_ids))

        except WebFault as e:
            raise api_exception(e.message)
