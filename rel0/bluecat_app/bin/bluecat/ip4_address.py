from entity import entity
from api_exception import api_exception

"""
IPv4 address obejcts.
"""


class ip4_address(entity):
    """Instantiate an ipv4_address.

    :param api: API instance used by the entity to communicate with BAM.
    :param soap_entity: the SOAP (suds) entity returned by the BAM API.
    :param soap_client: the suds client instance.

    """

    def __init__(self, api, soap_entity, soap_client):
        super(ip4_address, self).__init__(api, soap_entity, soap_client)

    """Get the address as a string.
    """

    def get_address(self):
        if not hasattr(self._properties, 'address'):
            raise api_exception('No IPv4 address found for address object')
        else:
            return self._properties['address']

    """Get the reverse name for the address.
    """

    def get_reverse_name(self):
        if self.get_address() == self._none_parameter:
            octets = ""
        else:
            octets = self.get_address().split('.')
        octets.reverse()
        return '.'.join(octets) + '.in-addr.arpa'
