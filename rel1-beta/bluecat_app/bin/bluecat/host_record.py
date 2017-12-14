import nsupdate
import util
from api_exception import api_exception
from deployment_role import deployment_role
from entity import entity


class host_record(entity):
    """Instantiate host record.

    :param api: API instance used by the entity to communicate with BAM.
    :param soap_entity: the SOAP (suds) entity returned by the BAM API.
    :param soap_client: the suds client instance.

    """

    def __init__(self, api, soap_entity, soap_client):
        super(host_record, self).__init__(api, soap_entity, soap_client)
        self._immutable_properties.append('addressIds')

    """Set the address(es) for a host record.

    :param addresses: list of addresses in the form of strings for the host record. E.g. ['192.168.0.1', '192.168.0.2'].

    """

    def set_addresses(self, addresses):
        self._properties['addresses'] = ','.join(addresses)

    """Get the addresses for a host record in the form of a list of strings.
    """

    def get_addresses(self):
        return self._properties['addresses'].split(',')

    """Get the owning configuration.
    """

    def get_configuration(self):
        return self.get_parent_of_type(entity.Configuration)

    """Get the parent zone.
    """

    def get_zone(self):
        return self.get_parent_of_type('Zone')

    """Get the IP4 address instances associated with the host record.
    """

    def get_ip4_addresses(self):
        c = self.get_parent_of_type(entity.Configuration)
        res = []
        for a in self.get_addresses():
            if util.is_valid_ipv4_address(a):
                res.append(c.get_ip4_address(a))
        return res

    """Get the IP6 address instances associated with the host record.
    """

    def get_ip6_addresses(self):
        c = self.get_parent_of_type(entity.Configuration)
        res = []
        for a in self.get_addresses():
            if util.is_valid_ipv6_address(a):
                res.append(c.get_ip6_address(a))
        return res

    """Get the owning view.
    """

    def get_view(self):
        return self.get_parent_of_type(entity.View)

    """Get the fully qualified domain name of the host record.
    """

    def get_full_name(self):
        return self._properties['absoluteName']

    """If there is a specific TTL set for the host record, return it, otherwise return -1.
    """

    def get_specific_ttl(self):
        if 'ttl' in self._properties:
            return int(self._properties['ttl'])
        else:
            return -1

    """Find the applicable TTL for the host record. This involves walking the entity tree in many cases.
    """

    def get_ttl(self, server=None):
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

    """Dynamically update the forward DNS space for a record. 

    :param tsig_key_file: file containing the TSIG key (if any) to use.

    """

    def dynamic_update_forward(self, tsig_key_file=None):
        # forward space
        for dr in self.get_deployment_roles(types=[deployment_role.MASTER, deployment_role.MASTER_HIDDEN]):
            s = dr.get_server()
            if s is not None:
                for server_ip in s.get_service_ip4_addresses():
                    for record_addr in self.get_addresses():
                        if util.is_valid_ipv4_address(record_addr):
                            nsupdate.update_a(server_ip, self.get_full_name(), record_addr, self.get_ttl(),
                                              tsig_key_file)
                        elif util.is_valid_ipv6_address(record_addr):
                            nsupdate.update_aaaa(server_ip, self.get_full_name(), record_addr, self.get_ttl(),
                                                 tsig_key_file)
                        else:
                            raise api_exception("invalid IP address", record_addr)

    """Dynamically update the reverse DNS space for a record. If there isn't a suitable deployment role set for the relevant network this
       method will do nothing.

    :param tsig_key_file: file containing the TSIG key (if any) to use.

    """

    def dynamic_update_reverse(self, tsig_key_file=None):
        # reverse space
        if self._properties['reverseRecord'] == 'true':
            for a in self.get_ip4_addresses():
                for dr in self.get_deployment_roles(types=[deployment_role.MASTER, deployment_role.MASTER_HIDDEN]):
                    s = dr.get_server()
                    if s is not None:
                        for server_ip in s.get_service_ip4_addresses():
                            nsupdate.create_ptr(server_ip, self.get_full_name(), a.get_reverse_name(), self.get_ttl(),
                                                tsig_key_file)
                        for server_ip in s.get_service_ip6_addresses():
                            nsupdate.create_ptr(server_ip, self.get_full_name(), a.get_reverse_name(), self.get_ttl(),
                                                tsig_key_file)

    """Dynamically delete the forward DNS space for a record. 

    :param tsig_key_file: file containing the TSIG key (if any) to use.

    """

    def dynamic_delete_forward(self, tsig_key_file=None):
        for dr in self.get_deployment_roles(types=[deployment_role.MASTER, deployment_role.MASTER_HIDDEN]):
            s = dr.get_server()
            if s is not None:
                for server_ip in s.get_service_ip4_addresses():
                    for record_addr in self.get_addresses():
                        if util.is_valid_ipv4_address(record_addr):
                            nsupdate.delete_a(server_ip, self.get_full_name(), tsig_key_file)
                        elif util.is_valid_ipv6_address(record_addr):
                            nsupdate.delete_aaaa(server_ip, self.get_full_name(), tsig_key_file)
                        else:
                            raise api_exception("invalid IP address", record_addr)

    """Dynamically delete the reverse DNS space for a record. If there isn't a suitable deployment role set for the relevant network this
       method will do nothing.

    :param tsig_key_file: file containing the TSIG key (if any) to use.

    """

    def dynamic_delete_reverse(self, tsig_key_file=None):
        if self._properties['reverseRecord'] == 'true':
            # reverse space
            for a in self.get_ip4_addresses():
                for dr in self.get_deployment_roles(types=[deployment_role.MASTER, deployment_role.MASTER_HIDDEN]):
                    s = dr.get_server()
                    if s is not None:
                        for server_ip in s.get_service_ip4_addresses():
                            nsupdate.delete_ptr(server_ip, a.get_reverse_name(), tsig_key_file)
                        for server_ip in s.get_service_ip6_addresses():
                            nsupdate.delete_ptr(server_ip, a.get_reverse_name(), tsig_key_file)

    """Dynamically create the forward DNS space for a record. 

    :param tsig_key_file: file containing the TSIG key (if any) to use.

    """

    def dynamic_create_forward(self, tsig_key_file=None):
        for dr in self.get_deployment_roles(types=[deployment_role.MASTER, deployment_role.MASTER_HIDDEN]):
            s = dr.get_server()
            if s is not None:
                for server_ip in s.get_service_ip4_addresses():
                    for record_addr in self.get_addresses():
                        if util.is_valid_ipv4_address(record_addr):
                            nsupdate.create_a(server_ip, self.get_full_name(), record_addr, self.get_ttl(),
                                              tsig_key_file)
                        elif util.is_valid_ipv6_address(record_addr):
                            nsupdate.create_aaaa(server_ip, self.get_full_name(), record_addr, self.get_ttl(),
                                                 tsig_key_file)
                        else:
                            raise api_exception("invalid IP address", record_addr)

    """Dynamically create the reverse DNS space for a record. If there isn't a suitable deployment role set for the relevant network this
       method will do nothing.

    :param tsig_key_file: file containing the TSIG key (if any) to use.

    """

    def dynamic_create_reverse(self, tsig_key_file=None):
        if self._properties['reverseRecord'] == 'true':
            for a in self.get_ip4_addresses():
                for dr in self.get_deployment_roles(types=[deployment_role.MASTER, deployment_role.MASTER_HIDDEN]):
                    s = dr.get_server()
                    if s is not None:
                        for server_ip in s.get_service_ip4_addresses():
                            nsupdate.create_ptr(server_ip, self.get_full_name(), a.get_reverse_name(), self.get_ttl(),
                                                tsig_key_file)
                        for server_ip in s.get_service_ip6_addresses():
                            nsupdate.create_ptr(server_ip, self.get_full_name(), a.get_reverse_name(), self.get_ttl(),
                                                tsig_key_file)
