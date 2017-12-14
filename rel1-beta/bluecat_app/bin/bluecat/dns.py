from suds import WebFault

import util
from api_exception import api_exception
from entity import entity

class dns(entity):
    """Base class for DNS objects
    """

    def __init__(self, api, soap_entity, soap_client):
        """Instantiate the base DNS class.

        :param api: API instance used by the entity to communicate with BAM.
        :param soap_entity: the SOAP (suds) entity returned by the BAM API.
        :param soap_client: the suds client instance.
        """
        super(dns, self).__init__(api, soap_entity, soap_client)

    def get_configuration(self):
        """Return the parent Configuration object.
        """
        return self.get_parent_of_type(entity.Configuration)

    def get_server_interface_id(self):
        return self._soap_entity['serverInterfaceId']

    def get_service(self):
        return self._soap_entity['service']

    def get_dns_deployment_option(self, option, server=None):
        e = self._soap_client.service.getDNSDeploymentOption(self.get_id(), option, 0)
        if not util.has_response(e):
            return None
        else:
            return entity(self, e, self._soap_client)

    def get_zone(self, name):
        """Get an immediate child zone by name without dot character.

        :param name: Name of the child zone.
        :return: Instance of the child zone or None
        """
        return self.get_child_by_name(name, entity.Zone)

    def get_zones(self, max_results=500):
        """Get all immediate child zones.

        :param max_results: Maximum number of zones to return. Default 500.
        :return: List of zone instances or empty List
        """
        return self.get_children_of_type(entity.Zone, max_results)

    def add_zone(self, absolute_name, deployable=False, template=0, **kwargs):
        """Adds DNS zones.

        You can use . (dot) characters to create the top level domain and subzones.

        :param absolute_name: Fully qualified name of the DNS zone to add (eg. example.com)
        :param deployable: boolean. Default False.
        :param template: ID of the associated network template
        :param kwargs: Keyword arguments of user-defined fields and values
        :return: zone instance of the new DNS zone
        """
        properties = 'deployable=true|' if deployable else 'deployable=false|'
        if template > 0:
            properties = properties + 'template=' + str(template) + '|'
        for k, v in kwargs.items():
            properties = properties + k + '=' + v + '|'

        return self._api.get_entity_by_id(
            self._soap_client.service.addZone(self.get_id(), absolute_name, properties))
