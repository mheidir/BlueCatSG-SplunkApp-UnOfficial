import util
from entity import entity

"""
IPv6 address obejcts.
"""


class ip6_address(entity):
    """Instantiate an ipv6_address.

    :param api: API instance used by the entity to communicate with BAM.
    :param soap_entity: the SOAP (suds) entity returned by the BAM API.
    :param soap_client: the suds client instance.

    """

    def __init__(self, api, soap_entity, soap_client):
        super(ip6_address, self).__init__(api, soap_entity, soap_client)

    """Get the address as a string.
    """

    def get_address(self):
        return self._properties['address']

    """Get the reverse name for the address.
    """

    def get_reverse_name(self):
        octets = util.ip6_cannonical(self.get_address().split(':'))
        octets.reverse()
        return '.'.join(octets) + '.in-addr.arpa'
