from suds import WebFault

import util
from api_exception import api_exception
from entity import entity


class resource_record(entity):
    """Base class for resource records

    :param api: API instance used by the entity to communicate with BAM.
    :param soap_entity: the SOAP (suds) entity returned by the BAM API.
    :param soap_client: the suds client instance.
    """

    def __init__(self, api, soap_entity, soap_client):
        super(resource_record, self).__init__(api, soap_entity, soap_client)

    def get_configuration(self):
        """Get the owning configuration.
        """
        return self.get_parent_of_type(entity.Configuration)

    def get_zone(self):
        """Get the parent zone.
        """
        return self.get_parent_of_type('Zone')

    def get_view(self):
        """Get the owning view.
        """
        return self.get_parent_of_type(entity.View)

    def get_full_name(self):
        """Get the fully qualified domain name of the resource record.
        """
        return self._properties['absoluteName']

    def get_specific_ttl(self):
        """If there is a specific TTL set for the resource record, return it, otherwise return -1.
        """
        if 'ttl' in self._properties:
            return int(self._properties['ttl'])
        else:
            return -1

    def get_ttl(self, server=None):
        """Find the applicable TTL for the resource record.

        This involves walking the entity tree in many cases.
        """
        if 'ttl' in self._properties:
            return int(self._properties['ttl'])

        if server is not None:
            # look for server specific option
            e = self.get_parent()
            while e is not None:
                try:
                    opt = self._soap_client.service.getDNSDeploymentOption(e.get_id(), 'zone-default-ttl',
                                                                           server.get_id())
                except WebFault as e:
                    raise api_exception(e.message)
                if util.has_response(opt):
                    return int(opt['value'])
                e = e.get_parent()

        # now look for option for any server
        e = self.get_parent()
        while e is not None:
            try:
                opt = self._soap_client.service.getDNSDeploymentOption(e.get_id(), 'zone-default-ttl', 0)
            except WebFault as e:
                raise api_exception(e.message)
            if util.has_response(opt):
                return int(opt['value'])
            e = e.get_parent()

        return 3600

    def move(self, resource_record_id, destination_zone):
        """Move resource record to a new zone.

        :param resource_record_id: The ID of the resource record to move.
        :param destination_zone: The FQDN of the destination zone.
        """
        try:
            self._soap_client.service.moveResourceRecord(resource_record_id, destination_zone)
        except WebFault as e:
            raise api_exception(e.message)

class alias_record(resource_record):
    """Instantiate alias CNAME record.

    :param api: API instance used by the entity to communicate with BAM.
    :param soap_entity: the SOAP (suds) entity returned by the BAM API.
    :param soap_client: the suds client instance.
    """

    def __init__(self, api, soap_entity, soap_client):
        super(alias_record, self).__init__(api, soap_entity, soap_client)

    def get_linked_record_name(self):
        """Get the linked record name
        """
        return self._properties['linkedRecordName']

class mx_record(resource_record):
    """Instantiate Mail Exchanger MX record.

    :param api: API instance used by the entity to communicate with BAM.
    :param soap_entity: the SOAP (suds) entity returned by the BAM API.
    :param soap_client: the suds client instance.
    """

    def __init__(self, api, soap_entity, soap_client):
        super(mx_record, self).__init__(api, soap_entity, soap_client)

    def get_linked_record_name(self):
        """Get the linked record name
        """
        return self._properties['linkedRecordName']

class text_record(resource_record):
    """Instantiate Text TXT record.

    :param api: API instance used by the entity to communicate with BAM.
    :param soap_entity: the SOAP (suds) entity returned by the BAM API.
    :param soap_client: the suds client instance.
    """

    def __init__(self, api, soap_entity, soap_client):
        super(text_record, self).__init__(api, soap_entity, soap_client)

class host_info_record(resource_record):
    """Instantiate Host Info HINFO record.

    :param api: API instance used by the entity to communicate with BAM.
    :param soap_entity: the SOAP (suds) entity returned by the BAM API.
    :param soap_client: the suds client instance.
    """

    def __init__(self, api, soap_entity, soap_client):
        super(host_info_record, self).__init__(api, soap_entity, soap_client)

class srv_record(resource_record):
    """Instantiate Service SRV record.

    :param api: API instance used by the entity to communicate with BAM.
    :param soap_entity: the SOAP (suds) entity returned by the BAM API.
    :param soap_client: the suds client instance.
    """

    def __init__(self, api, soap_entity, soap_client):
        super(srv_record, self).__init__(api, soap_entity, soap_client)

    def get_linked_record_name(self):
        """Get the linked record name
        """
        return self._properties['linkedRecordName']

class naptr_record(resource_record):
    """Instantiate Naming Authority Pointer Record NAPTR record.

    :param api: API instance used by the entity to communicate with BAM.
    :param soap_entity: the SOAP (suds) entity returned by the BAM API.
    :param soap_client: the suds client instance.
    """

    def __init__(self, api, soap_entity, soap_client):
        super(naptr_record, self).__init__(api, soap_entity, soap_client)

class external_host_record(resource_record):
    """Instantiate External Host record.

    :param api: API instance used by the entity to communicate with BAM.
    :param soap_entity: the SOAP (suds) entity returned by the BAM API.
    :param soap_client: the suds client instance.
    """

    def __init__(self, api, soap_entity, soap_client):
        super(external_host_record, self).__init__(api, soap_entity, soap_client)

class generic_record(resource_record):
    """Instantiate Generic record.

    The following generic record types are available: A, A6, AAAA, AFSDB,
    APL, CERT, DHCID, DNAME, DS, IPSECKEY, ISDN, KEY, KX, LOC,
    MB, MG, MINFO, MR, NS, NSAP, PTR, PX, RP, RT, SINK, SPF, SSHFP, WKS, and X25.
    These records contain name, type, and value information.
    :param api: API instance used by the entity to communicate with BAM.
    :param soap_entity: the SOAP (suds) entity returned by the BAM API.
    :param soap_client: the suds client instance.
    """

    def __init__(self, api, soap_entity, soap_client):
        super(generic_record, self).__init__(api, soap_entity, soap_client)
