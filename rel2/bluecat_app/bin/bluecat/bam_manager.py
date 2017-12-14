

# BlueCat API
from bluecat import api_exception, route, api, util

# App configuration
import config
import json
import os
import tempfile
import re
from suds import WebFault

from api import api

class bam_manager(object):
    """
    Create an object to manage connections to multiple BAMs
    """

    def __init__(self, url='', user='portalUser', password='portalUser'):
        self._user = user
        self._password = password
        self._url = url

    @staticmethod
    def write_to_file(dir_path='', api_dict={}, user=''):
        f = open(dir_path + 'bam_connections.json', 'w+')
        try:
            data = json.loads(f.read())
        except:
            data = {}
        f.close()
        for api_address in api_dict.keys():
            data[api_address] = True
        f, name = tempfile.mkstemp()
        os.write(f, json.dumps(data, indent=4, sort_keys=True))
        os.close(f)
        if (not os.path.isfile(dir_path + 'bam_connections.json')):
            os.rename(name, dir_path + 'bam_connections.json')
        else:
            os.rename(dir_path + 'bam_connections.json', dir_path + 'bam_connections_backup.json')
            os.rename(name, dir_path + 'bam_connections.json')
            os.remove(dir_path + 'bam_connections_backup.json')

    @staticmethod
    def login_to_api(ip_address, user):
        new_api = api(ip_address, sslverify=config.validate_server_cert)
        message = new_api.login(user.get_username(), user.get_password())
        user.add_api(new_api)
        return new_api

    @classmethod
    def search_bam(cls, ip_address, user=''):
        result = {}
        try:
            if user == '':
                raise api_exception('No user given!')
            ip_address = cls.create_valid_api_url(ip_address)
            if ip_address != '':
                for api_address in user.get_api_dict().keys():
                    if ip_address == api_address:
                        if not user.get_api_dict()[ip_address]:
                            cls.initialize_apis([ip_address], user)
                        return user.get_api_dict()[ip_address]
                new_api = cls.login_to_api(ip_address, user)
                cls.write_to_file(api_dict=user.get_api_dict(), user=user)
        except api_exception as e:
            return e.get_message()
        return new_api

    @classmethod
    def select_bam(cls, address, user=''):
        """
        Sets the BAM with the given address as the default BAM api used in workflows.

        :param address:
        :param user:
        :return:
        """
        result = {}
        try:
            address = cls.create_valid_api_url(address)
            if user == '':
                raise api_exception('No user given!')
            for api_address in user.get_api_dict().keys():
                if address == api_address:
                    if not user.get_api_dict()[address]:
                        new_api = cls.login_to_api(address, user)
                    user.set_api(address)
                    return True
            new_api = cls.login_to_api(address, user)
            user.set_api(address)
        except api_exception as e:
            return False
        return True

    @classmethod
    def initialize_apis(cls, address_list, user=''):
        try:
            if user == '':
                raise api_exception('No user given!')
            for address in address_list:
                address = cls.create_valid_api_url(address)
                try:
                    if not user.is_api_initialized(address):
                        new_api = cls.login_to_api(address, user)
                except:
                    pass
        except api_exception as e:
            return False
        return True

    @classmethod
    def create_valid_api_url(cls, url):
        address_parts = re.split('_|/', url)
        address = ''
        for part in address_parts:
            if util.validate_ipv4_address(part) or util.is_valid_domain_name(part):
                address = 'http://' + part + '/Services/API?wsdl'
                return address
        return ''
