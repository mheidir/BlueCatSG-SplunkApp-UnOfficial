from entity import entity
from bdds_server import server

"""
Deployment roles. There are multiple different types of role represented by the various string 'constants'
defined in the class body.
"""


class deployment_role(entity):
    MASTER = "MASTER"
    MASTER_HIDDEN = "MASTER_HIDDEN"
    SLAVE = "SLAVE"
    FORWARDER = "FORWARDER"
    NONE = "NONE"
    RECURSION = "RECURSION"
    SLAVE = "SLAVE"
    SLAVE_STEALTH = "SLAVE_STEALTH"
    STUB = "STUB"
    AD_MASTER = "AD_MASTER"

    """List of all role types.
    """
    roles = [MASTER, MASTER_HIDDEN, SLAVE, FORWARDER, NONE, RECURSION, SLAVE, SLAVE_STEALTH, STUB, AD_MASTER]

    """Instantiate a deployment role.

    :param api: API instance used by the entity to communicate with BAM.
    :param soap_entity: the SOAP (suds) entity returned by the BAM API.
    :param soap_client: the suds client instance.

    """

    def __init__(self, api, soap_entity, soap_client):
        super(deployment_role, self).__init__(api, soap_entity, soap_client)

    def get_server(self):
        """Get the server associated with a role or None if none exists.
        """
        try:
            e = self._soap_client.service.getServerForRole(self.get_id())
            if e == '':
                return None
            else:
                return server(self._api, e, self._soap_client)
        except WebFault as e:
            raise api_exception(e.message)

