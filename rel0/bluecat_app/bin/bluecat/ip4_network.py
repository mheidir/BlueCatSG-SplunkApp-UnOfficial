from suds import WebFault

import util
from api_exception import api_exception
from util import *
from entity import entity

"""
ip4_network instances. Networks are the leaves underneath blocks that contain IP addresses.
"""


class ip4_network(entity):
    """Instantiate an ipv4_network.

    :param api: API instance used by the entity to communicate with BAM.
    :param soap_entity: the SOAP (suds) entity returned by the BAM API.
    :param soap_client: the suds client instance.

    """

    def __init__(self, api, soap_entity, soap_client):
        super(ip4_network, self).__init__(api, soap_entity, soap_client)

    """Get the first N addresses of the network as a list.

    :param n: how many addresses to return.

    """

    def get_first_addresses(self, n):
        bits = self.get_properties()['CIDR'].split('/')
        mask = 0
        for x in range(0, int(bits[1])):
            mask |= 2 ** (31 - x)
        i = mask & util.ip42int(bits[0])
        res = []
        for x in range(0, n):
            res.append(util.int2ip4(i + x))
        return res

    """Get the next available IP4 address (as a string) optionally excluding a given list of addresses.

    :param exclude: which addresses (as a list of strings) to exclude.

    """

    def get_next_ip4_address_string(self, exclude=None):
        try:
            props = ''
            if exclude is not None:
                props = 'skip=' + ','.join(exclude)
            return self._soap_client.service.getNextIP4Address(self.get_id(), properties=props)
        except WebFault as e:
            raise api_exception(e.message)

    """Adds an IPv4 network using CIDR notation.

    :param cidr soap: the CIDR notation defining the network (for example, 10.10.10/24).
    :param properties: A string containing options.

    """

    def add_ip4_network(self, cidr, properties=''):
        try:
            properties = parse_properties(properties)
            return self._api.get_entity_by_id(self._soap_client.service.addIP4Network(self.get_id(), cidr, properties))
        except WebFault as e:
            raise api_exception(e.message)