from dns import dns

class zone(dns):
    """Instantiate a DNS Zone object

    :param api: API instance used by the entity to communicate with BAM.
    :param soap_entity: the SOAP (suds) entity returned by the BAM API.
    :param soap_client: the suds client instance.
    """

    def __init__(self, api, soap_entity, soap_client):
        super(zone, self).__init__(api, soap_entity, soap_client)

    def get_full_name(self):
        return self._properties['absoluteName']
