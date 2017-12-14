from suds import WebFault

import util
from api_exception import api_exception
from dns import dns


class view(dns):
    """A DNS View
    """

    def __init__(self, api, soap_entity, soap_client):
        """Instantiate a DNS View object

        :param api: API instance used by the entity to communicate with BAM.
        :param soap_entity: the SOAP (suds) entity returned by the BAM API.
        :param soap_client: the suds client instance.
        """
        super(view, self).__init__(api, soap_entity, soap_client)

    def add_resource_record(self, absolute_name, type, rdata, ttl=-1, properties={}):
        """Generic method for adding resource records of any type.

        :param absolute_name: The absolute name of the record, specified as an FQDN. If you are adding a
            record in a zone that is linked to a incremental Naming Policy, a single hash (#)
            sign must be added at the appropriate location in the FQDN. Depending on the
            policy order value, the location of the single hash (#) sign varies.
        :param type: The type of record being added. Supported types using this method:
            AliasRecord
            HINFORecord
            HostRecord
            MXRecord
            TXTRecord
        :param rdata: The data for the resource record in BIND format (for example, for A records,
            A 10.0.0.4). You can specify either a single IPv4 or IPv6 address for the record.
        :param ttl: The time-to-live value for the record.
        :param properties: Adds object properties, including user-defined fields.
        :return: An instance of the resource record type that was added.
        """
        supported_types = [
            self.AliasRecord,
            self.HINFORecord,
            self.HostRecord,
            self.MXRecord,
            self.TXTRecord
        ]
        if type not in supported_types:
            raise api_exception('Type %s is not supported by this method' % type)

        try:
            self._api.get_entity_by_id(
                self._soap_client.service.addResourceRecord(self.get_id(), absolute_name, type, rdata, ttl,
                                                            util.parse_properties(properties))
            )
        except WebFault as e:
            raise api_exception(e.message)

    def add_host_record(self, absolute_name, addresses, ttl=-1, properties={}):
        try:

            return self._api.get_entity_by_id(
                self._soap_client.service.addHostRecord(self.get_id(), absolute_name, ','.join(addresses), ttl,
                                                        util.parse_properties(properties)))

        except WebFault as e:
            raise api_exception(e.message)

    def get_resource_record(self, absolute_name, type):
        """Get a resource record of the specified type.

        :param absolute_name: The FQDN of the resource record to get.
        :param type: The type of resource record to get.
        :return: An instance of the specified resource record type.
        """
        try:
            bits = absolute_name.split('.')
            bits.reverse()
            e = self
            for i in range(0, len(bits) + 1):
                last = bits[i:]
                last.reverse()
                rr = e.get_child_by_name('.'.join(last), type)
                if rr:
                    return rr
                else:
                    e = e.get_child_by_name(bits[i], self.Zone)
                    if e is None:
                        break
            return None
        except WebFault as e:
            raise api_exception(e.message)

    def get_host_record(self, absolute_name):
        """Get a host record.

        :param absolute_name: The FQDN of the host record to get.
        :return: An instance of host_record.
        """
        return self.get_resource_record(absolute_name, self.HostRecord)

    def get_alias_record(self, absolute_name):
        """Get an alias record.

        :param absolute_name: The FQDN of the host record to get.
        :return: An instance of alias_record.
        """
        return self.get_resource_record(absolute_name, self.AliasRecord)

    def get_mx_record(self, absolute_name):
        """Get a MX record.

        :param absolute_name: The FQDN of the host record to get.
        :return: An instance of mx_record.
        """
        return self.get_resource_record(absolute_name, self.MXRecord)

    def get_text_record(self, absolute_name):
        """Get a text record.

        :param absolute_name: The FQDN of the host record to get.
        :return: An instance of text_record.
        """
        return self.get_resource_record(absolute_name, self.TXTRecord)

    def get_hinfo_record(self, absolute_name):
        """Get a host info record.

        :param absolute_name: The FQDN of the host record to get.
        :return: An instance of host_info_record.
        """
        return self.get_resource_record(absolute_name, self.HINFORecord)

    def get_srv_record(self, absolute_name):
        """Get a SRV record.

        :param absolute_name: The FQDN of the host record to get.
        :return: An instance of srv_record.
        """
        return self.get_resource_record(absolute_name, self.SRVRecord)

    def get_naptr_record(self, absolute_name):
        """Get a NAPTR record.

        :param absolute_name: The FQDN of the host record to get.
        :return: An instance of naptr_record.
        """
        return self.get_resource_record(absolute_name, self.NAPTRRecord)

    def get_external_host_record(self, absolute_name):
        """Get an external host record.

        :param absolute_name: The FQDN of the host record to get.
        :return: An instance of external_host_record.
        """
        return self.get_resource_record(absolute_name, self.ExternalHostRecord)

    def get_generic_record(self, absolute_name):
        """Get a generic record.

        :param absolute_name: The FQDN of the host record to get.
        :return: An instance of generic_record.
        """
        return self.get_resource_record(absolute_name, self.GenericRecord)

    def add_alias_record(self, absolute_name, linked_record, ttl=-1, properties={}):
        """Add a new CNAME record for an existing host record.

        This method adds the record under a zone.

        :param absolute_name: The FQDN of the alias. If you are adding a record in a zone that is linked to a
            incremental Naming Policy, a single hash (#) sign must be added at the
            appropriate location in the FQDN. Depending on the policy order value, the
            location of the single hash (#) sign varies.
        :param linked_record: The name of the record to which this alias will link.
        :param ttl: The time-to-live value for the record. TTL is ignored by default.
        :param properties: Adds object properties, including comments and user-defined fields.
        :return: An instance of alias_record.
        """
        try:
            return self._api.get_entity_by_id(
                self._soap_client.service.addAliasRecord(self.get_id(), absolute_name, linked_record,
                                                         ttl, util.parse_properties(properties))
            )
        except WebFault as e:
            raise api_exception(e.message)

    def get_aliases_by_hint(self, start, count, hint, retrieveFields=False):
        """Get a list of alias records that matches hint.

        :param start: Indicates where in the list of objects to start returning objects. The list begins at
            an index of 0.
        :param count: The maximum number of child objects that this method will return. The value
            must be less than or equal to 10.
        :param hint: The following wildcards are supported in the hint option:
            ^-matches the beginning of a string. For example: ^ex matches example but not text.
            $-matches the end of a string. For example: ple$ matches example but not please.
            ^ $-matches the exact characters between the two wildcards. For example: ^example$ only matches example.
            ?-matches any one character. For example: ex?t matches exit.
            *-matches one or more characters within a string. For example: ex*t matches exit and excellent.
        :param retrieveFields: Include UDF in results.
        :return: A List of alias_records.
        """
        retrieveFields = 'true' if retrieveFields else 'false'
        try:
            res_list = self._soap_client.service.getAliasesByHint(start, count, 'hint=%s|retrieveFields=%s' % (hint, retrieveFields))
            if not util.has_response(res_list):
                return None
            else:
                a_list = []
                for item in res_list.item:
                    a_list.append(self._api.instantiate_entity(item, self._soap_client))

                return a_list
        except WebFault as e:
            raise api_exception(e.message)

    def add_external_host_record(self, absolute_name, properties={}):
        """Add a new External Host record.

        This method adds the record under a zone.

        :param absolute_name: FQDN for the host record.
        :param properties: Adds object properties, including comments and user-defined fields.
        :return: An instance of external_host_record.
        """
        try:
            return self._api.get_entity_by_id(
                self._soap_client.service.addExternalHostRecord(self.get_id(), absolute_name,
                                                         util.parse_properties(properties))
            )
        except WebFault as e:
            raise api_exception(e.message)

    def add_mx_record(self, absolute_name, priority, linked_record_name, ttl=-1, properties={}):
        """Add a new Mail Exchanger MX record.

        This method adds the record under a zone.

        :param absolute_name: The FQDN for the record. If you are adding a record in a zone that is linked
            to a incremental Naming Policy, a single hash (#) sign must be added at the
            appropriate location in the FQDN. Depending on the policy order value, the
            location of the single hash (#) sign varies.
        :param priority: Specifies which mail server to send clients to first when multiple matching MX
            records are present. Multiple MX records with equal priority values are referred
            to in a round-robin fashion.
        :param ttl: The time-to-live value for the record. TTL is ignored by default.
        :param properties: Adds object properties, including comments and user-defined fields.
        :return: An instance of mx_record.
        """
        try:
            return self._api.get_entity_by_id(
                self._soap_client.service.addMXRecord(self.get_id(), absolute_name, priority, linked_record_name,
                                                      ttl, util.parse_properties(properties))
            )
        except WebFault as e:
            raise api_exception(e.message)

    def add_text_record(self, absolute_name, txt, ttl=-1, properties={}):
        """Add a new TEXT TXT record.

        This method adds the record under a zone.

        :param absolute_name: The FQDN of the text record. If you are adding a record in a zone that is linked
            to a incremental Naming Policy, a single hash (#) sign must be added at the
            appropriate location in the FQDN. Depending on the policy order value, the
            location of the single hash (#) sign varies.
        :param txt: The text data for the record.
        :param ttl: The time-to-live value for the record. TTL is ignored by default.
        :param properties: Adds object properties, including comments and user-defined fields.
        :return: An instance of text_record.
        """
        try:
            return self._api.get_entity_by_id(
                self._soap_client.service.addTXTRecord(self.get_id(), absolute_name, txt, ttl,
                                                       util.parse_properties(properties))
            )
        except WebFault as e:
            raise api_exception(e.message)

    def add_hinfo_record(self, absolute_name, cpu, os, ttl=-1, properties={}):
        """Add a new Host Info HINFO record.

        :param absolute_name: The FQDN of the HINFO record. If you are adding a record in a zone that is
            linked to a incremental Naming Policy, a single hash (#) sign must be added at
            the appropriate location in the FQDN. Depending on the policy order value, the
            location of the single hash (#) sign varies.
        :param cpu: A string providing central processing unit information.
        :param os: A string providing operating system information.
        :param ttl: The time-to-live value for the record. TTL is ignored by default.
        :param properties: Adds object properties, including comments and user-defined fields.
        :return: An instance of host_info_record.
        """
        try:
            return self._api.get_entity_by_id(
                self._soap_client.service.addHINFORecord(self.get_id(), absolute_name, cpu, os,
                                                         ttl, util.parse_properties(properties))
            )
        except WebFault as e:
            raise api_exception(e.message)

    def add_srv_record(self, absolute_name, priority, port, weight, linked_record_name, ttl=-1, properties={}):
        """Add a new SRV record.

        This method adds the record under a zone.

        :param absolute_name: The FQDN of the SRV record. If you are adding a record in a zone that
            is linked to a incremental Naming Policy, a single hash (#) sign must be
            added at the appropriate location in the FQDN. Depending on the policy
            order value, the location of the single hash (#) sign varies.
        :param priority: Specifies which SRV record to use when multiple matching SRV records
            are present. The record with the lowest value takes precedence.
        :param port: The TCP/UDP port on which the service is available.
        :param weight: If two matching SRV records within a zone have equal priority, the weight
            value is checked. If the weight value for one object is higher than the other,
            the record with the highest weight has its resource records returned first.
        :param linked_record_name: The FQDN of the host record to which this SRV record is linked.
        :param ttl: The time-to-live value for the record. TTL is ignored by default.
        :param properties: Adds object properties, including comments and user-defined fields.
        :return: An instance of srv_record.
        """
        try:
            return self._api.get_entity_by_id(
                self._soap_client.service.addSRVRecord(self.get_id(), absolute_name, priority, port,
                                                       weight, linked_record_name, ttl,
                                                       util.parse_properties(properties))
            )
        except WebFault as e:
            raise api_exception(e.message)

    def add_naptr_record(self, absolute_name, order, preference, service, regexp, replacement, flags, ttl=-1, properties={}):
        """Add a new NAPTR record.

        :param absolute_name: The FQDN for the record. If you are adding a record in a zone that is linked
            to a incremental Naming Policy, a single hash (#) sign must be added at the
            appropriate location in the FQDN. Depending on the policy order value, the
            location of the single hash (#) sign varies.
        :param order: Specifies the order in which NAPTR records are read if several are present and
            are possible matches. The lower ordervalue takes precedence.
        :param preference: Specifies the order in which NAPTR records are read if the ordervalues are the
            same in multiple records. The lower preferencevalue takes precedence.
        :param service: Specifies the service used for the NAPTR record. Valid settings for this
            parameter are listed in ENUM Services on page 192 in BAM API Guide.
        :param regexp: A regular expression, enclosed in double quotation marks, used to transform
            the client data. If a regular expression is not specified, a domain name must be
            specified in the replacement parameter.
        :param replacement: Specifies a domain name as an alternative to the regexp. This parameter
            replaces client data with a domain name.
        :param flags: An optional parameter used to set flag values for the record.
        :param ttl: The time-to-live value for the record. TTL is ignored by default.
        :param properties: Adds object properties, including comments and user-defined fields.
        :return: An instance of naptr_record.
        """
        try:
            return self._api.get_entity_by_id(
                self._soap_client.service.addNAPTRRecord(self.get_id(), absolute_name, order, preference,
                                                       service, regexp, replacement, flags, ttl,
                                                       util.parse_properties(properties))
            )
        except WebFault as e:
            raise api_exception(e.message)

    def add_generic_record(self, absolute_name, type, rdata, ttl=-1, properties={}):
        """Add a new Generic record of specified type.

        :param absolute_name: The FQDN of the record. If you are adding a record in a zone that is linked
            to a incremental Naming Policy, a single hash (#) sign must be added at the
            appropriate location in the FQDN. Depending on the policy order value, the
            location of the single hash (#) sign varies.
        :param type: The type of record being added. Valid settings for this parameter are the
            generic resource record types supported in Address Manager: A6, AAAA,
            AFSDB, APL, CERT, DNAME, DNSKEY, DS, ISDN, KEY, KX, LOC, MB,
            MG, MINFO, MR, NS, NSAP, PX, RP, RT, SINK, SSHFP, WKS, and X25.
        :param rdata: The data for the resource record in BIND format (for example, for A records,
            A 10.0.0.4).
        :param ttl: The time-to-live value for the record. TTL is ignored by default.
        :param properties: Adds object properties, including comments and user-defined fields.
        :return: An instance of generic_record.
        """
        try:
            return self._api.get_entity_by_id(
                self._soap_client.service.addGenericRecord(self.get_id(), absolute_name, type, rdata,
                                                       ttl, util.parse_properties(properties))
            )
        except WebFault as e:
            raise api_exception(e.message)

    def add_enum_zone(self, prefix, deployable=False, **properties):
        """Add a new ENUM zone.

        :param prefix: The number prefix for the ENUM zone.
        :param deployable: Sets whether this zone is deployable. Default is False.
        :param properties: Adds object properties, including user-defined fields.
        :return: An instance of ENUM zone.
        """
        properties['deployable'] = 'true' if deployable else 'false'
        try:
            return self._api.get_entity_by_id(
                self._soap_client.service.addEnumZone(self.get_id(), prefix,
                                                      util.parse_properties(properties))
            )
        except WebFault as e:
            raise api_exception(e.message)

    def get_enum_zone(self, prefix):
        """Get Enum Zone with the specified prefix.

        :param prefix:
        :return: An enum_zone instance.
        """
        return self.get_child_by_name(prefix, self.EnumZone)

    def get_enum_zones(self):
        """Get list of all enum zones in this View
        """
        return self.get_children_of_type(self.EnumZone)