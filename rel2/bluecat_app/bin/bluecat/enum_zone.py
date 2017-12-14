from collections import namedtuple
from suds import WebFault

from api_exception import api_exception
from entity import entity
import util


class enum_zone(entity):
    """An ENUM Zone object in BAM

    ENUM zones provide voice over IP (VoIP) functionality within a DNS server.
    The system requires DNS to manage the phone numbers associated with client end points; Address
    Manager provides an E164 or ENUM zone type for this purpose. The ENUM zone represents the area
    code for the phone prefixes and numbers stored in it. ENUM zones contain special sub-zones called
    prefixes that represent telephone exchanges and can contain the records for the actual devices.
    VoIP devices are addressed in several ways. A uniform resource identifier (URI) string provides custom
    forward locator references for these devices as covered in RFC 3401. Reverse DNS is used to discover
    the relevant information for a device based on its phone number. Name authority pointer (NAPTR) records
    are used to represent this information.
    """
    
    ServiceData = namedtuple('ServiceData', 'service, uri, comment, ttl')
    ServiceType = namedtuple('ServiceType',
                             "H323, \
                             SIP, \
                             ifax_mailto, \
                             pres, \
                             web_http, \
                             web_https, \
                             ft_ftp, \
                             email_mailto, \
                             fax_tel, \
                             sms_tel, \
                             sms_mailto, \
                             ems_tel, \
                             ems_mailto, \
                             mms_tel, \
                             mms_mailto, \
                             VPIM_MAILTO, \
                             VPIM_LDAP, \
                             voice_tel, \
                             pstn_tel, \
                             pstn_sip, \
                             xmpp, \
                             im"
                             )

    service_type = ServiceType(
        'H323',
        'SIP',
        'ifax mailto',
        'pres',
        'web http',
        'web https',
        'ft ftp',
        'email mailto',
        'fax tel',
        'sms tel',
        'sms mailto',
        'ems tel',
        'ems mailto',
        'mms tel',
        'mms mailto',
        'VPIM MAILTO',
        'VPIM LDAP',
        'voice tel',
        'pstn tel',
        'pstn sip',
        'xmpp',
        'im'
    )

    def __init__(self, api, soap_entity, soap_client):
        """Instantiate an ENUM Zone object.

        :param api:
        :param soap_entity:
        :param soap_client:
        """
        super(enum_zone, self).__init__(api, soap_entity, soap_client)

    def create_service_data(self, service_type, uri, comment='', ttl=-1):
        """

        :param service_type:
        :param uri:
        :param comment:
        :param ttl:
        :return:
        """
        return self.ServiceData(service_type, uri, comment, ttl)

    def add_enum_number(self, number, service_data, name='', **properties):
        """Add an ENUM number object to the ENUM zone.

        :param number: The ENUM phone number.
        :param service_data: List of enum_number.ServiceData objects.
        :param name: Optional name for the ENUM number.
        :param properties: Adds object properties, including user-defined fields.
        :return: An instance of the new enum_number.
        """
        data = ''
        for d in service_data:
            data = ','.join([str(x) for x in d]) + ','

        properties['data'] = data
        if name:
            properties['name'] = name

        try:
            return self._api.get_entity_by_id(
                self._soap_client.service.addEnumNumber(self.get_id(), number,
                                                        util.parse_properties(properties))
            )
        except WebFault as e:
            raise api_exception(e.message)

    def get_enum_number(self, number):
        """Get an EnumNumber object

        :param number: The number of the EnumNumber object.
        :return An instance of enum_number.
        """
        return self.get_child_by_name(number, self.EnumNumber)

    def get_enum_numbers(self):
        """Get List of EnumNumber objects."""
        return self.get_children_of_type(self.EnumNumber)

class enum_number(entity):
    """An ENUM number in BAM

    ENUM number objects represent VoIP phone numbers within Address Manager. This functionality is
    provided as an alternative to using raw NAPTR records.
    """

    def __init__(self, api, soap_entity, soap_client):
        """Instantiate an ENUM Number object.

        :param api:
        :param soap_entity:
        :param soap_client:
        """
        super(enum_number, self).__init__(api, soap_entity, soap_client)

class service_type(object):
    """Services supported by ENUM number objects"""

    H323 = 'H323'
    SIP = 'SIP'
    ifax_mailto = 'ifax mailto'
    pres = 'pres'
    web_http = 'web http'
    web_https = 'web https'
    ft_ftp = 'ft ftp'
    email_mailto = 'email mailto'
    fax_tel = 'fax tel'
    sms_tel = 'sms tel'
    sms_mailto = 'sms mailto'
    ems_tel = 'ems tel'
    ems_mailto = 'ems mailto'
    mms_tel = 'mms tel'
    mms_mailto = 'mms mailto'
    VPIM_MAILTO = 'VPIM MAILTO'
    VPIM_LDAP = 'VPIM LDAP'
    voice_tel = 'voice tel'
    pstn_tel = 'pstn tel'
    pstn_sip = 'pstn sip'
    xmpp = 'xmpp'
    im = 'im'
