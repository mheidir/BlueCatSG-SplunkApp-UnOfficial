import socket
import struct
import os
import json
import sys
import tempfile
import random
import re
#from paramiko import SSHClient, AutoAddPolicy

from api_exception import api_exception


def properties_to_map(properties):
    """ Turn a string of BAM properties into a dictionary of name->value.

    :param: properties: string in the form 'a=b|c=d|...'
    """
    res = {}
    for props in properties.split('|'):
        if props != '':
            bits = props.split('=')
            if len(bits) == 2:
                res[bits[0]] = bits[1]
            else:
                raise api_exception('malformed properties string', bits)
    return res

def map_to_properties(map):
    """ Turn a dictionary of properties into a BAM propery string.
    """
    res = []
    for k, v in map.items():
        res.append(k + '=' + v)
    return '|'.join(res)

def is_valid_ipv4_address(address):
    """ Figure out if a string is a valid IPv4 address.
    """
    try:
        socket.inet_pton(socket.AF_INET, address)
        return True
    except socket.error:
        return False


def validate_ipv4_address(address):
    """ Alternate IPv4 address validator.
    """
    address_parts = address.split('.')
    if len(address_parts) == 4:
        if 255 < int(address_parts[0])  or int(address_parts[0]) < 0:
            return False
        for i in range(1, 4):
            if 255 < int(address_parts[i])  or int(address_parts[i]) < 0:
                return False
        return True
    return False

def is_valid_ipv6_address(address):
    """ Figure out if a string is a valid IPv6 address.
    """
    try:
        socket.inet_pton(socket.AF_INET6, address)
        return True
    except socket.error:  # not a valid address
        return False

def ip42int(addr):
    """ Turn an IP address string into a 32 bit integer.
    """
    return struct.unpack("!I", socket.inet_aton(addr))[0]


def int2ip4(addr):
    """ Turn a 32 bit integer into an IP4 address string.
    """
    return socket.inet_ntoa(struct.pack("!I", addr))

def is_valid_domain_name(address):
    try:
       valid_address = re.compile(r'^(([a-z\d]([a-z\d-]*[a-z\d])*)\.)+[a-z]{2,}$')
       matching_address = valid_address.match(address)
       if matching_address and address == matching_address.group(0):
           return True
       else:
           return False
    except:
        pass

def get_api_list(path):
    api_list = {}
    if os.path.isfile(path):
        f = open(path)
        try:
            bam_addresses = json.loads(f.read())
        except:
            bam_addresses = {}
        for address in bam_addresses.keys():
            api_list[address] = False
        f.close()
    return api_list

def has_response(response, version='0.0.0'):
    """
    Check for none response for anything that you would normally expect to return an entity.
    :param response:
    :param version:
    :return:
    """

    if 'id' not in response:
        try:
            return has_response(response[0])
        except:
            return False
    elif response['id'] == 0:
        return False
    else:
        return True

def parse_properties(properties, version='0.0.0'):
    """
    Parses property input that is in a list or dictionary form and converts it to a string of property=value
    separated by '|' pipe characters

    :param properties:
    :return:


    """
    if properties:
        if isinstance(properties, basestring):
            if not properties.endswith('|'):
                properties = properties + '|'
            valid_properties = re.compile(r'^([a-z\d]+=[a-z_ /\.\d]+\|)*$', re.IGNORECASE)
            matching_address = valid_properties.match(properties)
            if matching_address and properties == matching_address.group(0):
                return properties
            else:
                raise api_exception('The properties String given is not in a valid format!')
        try:
            property_list = ['%s=%s' % (k, properties[k]) for k in properties]
            return '|'.join(property_list) + '|'
        except:
            return '|'.join(properties) + '|'
    else:
        return ''

def map_function_to_api_classes(api_obj_list, function, bams=[], bams_parameters={}, log='', *args, **kwargs):
    """
    Use to call the same function in multiple different api objects, can be on same BAM or different BAMs.

    :param classes:             A list of api objects whose function you wish to call
    :param function:            The function you want to call
    :param bams:                The list of BAMs which you allow the function to run on
    :param bams_parameters:     If you only want to pass parameters to specific BAMs instead of all BAMs, you specify
                                the custom parameters for each BAM in a dictionary format, do not add a BAM to the dict
                                if there are no custom parameters for the BAM
    :param args:                Default parameters for each function
    :param kwargs:              Default keyword parameters for each function
    :return:                    A dictionary of bam address : function result
    """
    results = {}
    for api_object in api_obj_list:
        try:
            api_url = api_object.get_url()
            if bams and api_url in bams:
                if not api_url in bams_parameters:
                    bams_parameters[api_url] = args
                if api_url in results:
                    try:
                        results[api_url] = results[api_url] + [getattr(api_object, function)(*bams_parameters[api_url], **kwargs)]
                    except:
                        results[api_url] = [results[api_url]] + [getattr(api_object, function)(*bams_parameters[api_url], **kwargs)]
                else:
                    results[api_url] = getattr(api_object, function)(*bams_parameters[api_url], **kwargs)
        except BaseException as e:
            if log:
                log.info('For api url: %s got error: %s' % (api_url, e))
            pass
    return results

def remove_from_bam_control(ip, username='', password=''):
    """Not Tested! Removes a BDDS from BAM control

    :param username: The administrator username of the BDDS
    :param password: The administrator password of the BDDS
    :param ip: IP address of the BDDS
    :return: False if there is an error removing from control. True otherwise.
    """
    cmd = '/usr/local/bluecat/PsmClient node set proteus-control=0'
    output, error = run_ssh_cmd(ip, username, password, cmd)
    if 'retcode=ok' in output:
        print 'BDDS %s removed from BAM control.' % ip
        return True
    else:
        print 'BDDS %s failed to be removed from BAM control. Output was:\n%s' % (ip, output)
        return False

def run_ssh_cmd(hostname, username='', password='', cmd='', timeout=30, **kwargs):
    """Execute a single SSH command.

    :param hostname: Hostname or IP4/IP6 address of the remote server.
    :param username: Username to login to remote server if no key found
    :param password: Password to login to remote server if no key found
    :param cmd: One-liner command to execute on remote system via SSH
    :param timeout: Time to wait for command to execute.
    :param kwargs: Additional keyword arguments supported by paramiko.SSHClient.connect().
    :return: A tuple: stdout, stderr.
    """
#    ssh = SSHClient()
#    ssh.set_missing_host_key_policy(AutoAddPolicy())
#    try:
#        ssh.connect(hostname, username=username, password=password, timeout=10, **kwargs)
#    except:
#        e = sys.exc_info()[1]
#        #logger.error('Exception trying to connect to server %s:\n%s' % (hostname,e))
#        raise e

#    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
#    output, error = stdout.read(), stderr.read()
#    ssh.close()
#    return output, error
