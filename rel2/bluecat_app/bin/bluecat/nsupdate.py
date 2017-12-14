import os
import subprocess
import warnings

from api_exception import api_exception

"""
Various functions for peforming dynamic DNS operations via nsupdate. There are Python modules to do this directly
but it's not clear how well debugged these are hence sticking to running nsupdate.
"""

# Ignore warnings about tmpnam being potentially insecure, this is reasonable given the environment this code will run in.
warnings.filterwarnings('ignore', 'tmpnam')

"""Run an nsupdate command file optionally using a TSIG key.

    :param command_file: The name of a file containing some nsupdate commands.
    :param tsig_key_file: The name of TSIG key file (can be None).

"""


def run_nsupdate(command_file, tsig_key_file=None):
    try:
        if tsig_key_file is not None:
            subprocess.check_output(['nsupdate', '-k', tsig_key_file, '-v', command_file], stderr=subprocess.STDOUT,
                                    shell=False)
        else:
            subprocess.check_output(['nsupdate', '-v', command_file], stderr=subprocess.STDOUT, shell=False)
        os.unlink(command_file)
    except subprocess.CalledProcessError as e:
        os.unlink(command_file)
        raise api_exception('nsupdate failed:' + e.output.strip())


"""Dynamically create a host record.

    :param type: the type of host record ('a' or 'aaaa')
    :param server_ip: the IP address of the DNS server on which to create the record.
    :param name: the name of the new record to create.
    :param address: the address of the new record to create.
    :param ttl: the TTL of the new record to create.
    :param tsig_key_file: the name of the optional TSIG key file to use.

"""


def create_host_record(type, server_ip, name, addr, ttl, tsig_key_file=None):
    fn = os.tmpnam()
    f = open(fn, 'w')
    f.write('server %s\n' % server_ip)
    f.write('update add %s %s %s %s\n' % (name, ttl, type, addr))
    f.write('send\n')
    f.close()
    run_nsupdate(fn, tsig_key_file)


"""Dynamically update a host record.

    :param type: the type of host record ('a' or 'aaaa')
    :param server_ip: the IP address of the DNS server on which to update the record.
    :param name: the name of the record to update.
    :param address: the new address of the record.
    :param ttl: the new TTL of the record to update.
    :param tsig_key_file: the name of the optional TSIG key file to use.

"""


def update_host_record(type, server_ip, name, addr, ttl, tsig_key_file=None):
    fn = os.tmpnam()
    f = open(fn, 'w')
    f.write('server %s\n' % server_ip)
    # delete then add rather than just update to cope with records that don't already exist
    f.write('update delete %s a\n' % name)
    f.write('update add %s %s %s %s\n' % (name, ttl, type, addr))
    f.write('send\n')
    f.close()
    run_nsupdate(fn, tsig_key_file)


"""Dynamically delete a host record.

    :param type: the type of host record ('a' or 'aaaa')
    :param server_ip: the IP address of the DNS server on which to delete the record.
    :param name: the name of the record to delete.
    :param tsig_key_file: the name of the optional TSIG key file to use.

"""


def delete_host_record(type, server_ip, name, tsig_key_file):
    fn = os.tmpnam()
    f = open(fn, 'w')
    f.write('server %s\n' % server_ip)
    f.write('update delete %s %s\n' % (name, type))
    f.write('send\n')
    f.close()
    run_nsupdate(fn, tsig_key_file)


"""Dynamically update an A record.

    :param server_ip: the IP address of the DNS server on which to update the record.
    :param name: the name of the record to update.
    :param address: the new address of the record to update.
    :param ttl: the new TTL of the record to update.
    :param tsig_key_file: the name of the optional TSIG key file to use.

"""


def update_a(server_ip, name, addr, ttl, tsig_key_file=None):
    update_host_record('a', server_ip, name, addr, ttl, tsig_key_file)


"""Dynamically update an AAAA record.

    :param server_ip: the IP address of the DNS server on which to update the record.
    :param name: the name of the record to update.
    :param address: the new address of the record to update.
    :param ttl: the new TTL of the record to update.
    :param tsig_key_file: the name of the optional TSIG key file to use.

"""


def update_aaaa(server_ip, name, tsig_key_file=None):
    update_host_record('aaaa', server_ip, name, addr, ttl, tsig_key_file)


"""Dynamically create an A record.

    :param server_ip: the IP address of the DNS server on which to create the record.
    :param name: the name of the new record to create.
    :param address: the address of the new record to create.
    :param ttl: the TTL of the new record to create.
    :param tsig_key_file: the name of the optional TSIG key file to use.

"""


def create_a(server_ip, name, addr, ttl, tsig_key_file=None):
    create_host_record('a', server_ip, name, addr, ttl, tsig_key_file)


"""Dynamically create an AAAA record.

    :param server_ip: the IP address of the DNS server on which to create the record.
    :param name: the name of the new record to create.
    :param address: the address of the new record to create.
    :param ttl: the TTL of the new record to create.
    :param tsig_key_file: the name of the optional TSIG key file to use.

"""


def create_aaaa(server_ip, name, tsig_key_file=None):
    create_host_record('aaaa', server_ip, name, addr, ttl, tsig_key_file)


"""Dynamically delete an A record.

    :param server_ip: the IP address of the DNS server on which to delete the record.
    :param name: the name of the record to delete.
    :param tsig_key_file: the name of the optional TSIG key file to use.

"""


def delete_a(server_ip, name, tsig_key_file=None):
    delete_host_record('a', server_ip, name, tsig_key_file)


"""Dynamically delete an AAAA record.

    :param server_ip: the IP address of the DNS server on which to delete the record.
    :param name: the name of the record to delete.
    :param tsig_key_file: the name of the optional TSIG key file to use.

"""


def delete_aaaa(server_ip, name, tsig_key_file=None):
    delete_host_record('aaaa', server_ip, name, tsig_key_file)


"""Dynamically create a PTR record.

    :param server_ip: the IP address of the DNS server on which to create the record.
    :param name: the name of the new record to create.
    :param reverse_name: the reverse space name of the new record to create.
    :param ttl: the TTL of the new record to create.
    :param tsig_key_file: the name of the optional TSIG key file to use.

"""


def create_ptr(server_ip, name, reverse_name, ttl, tsig_key_file=None):
    fn = os.tmpnam()
    f = open(fn, 'w')
    f.write('server %s\n' % server_ip)
    f.write('update add %s %s ptr %s\n' % (reverse_name, ttl, name))
    f.write('send\n')
    f.close()
    run_nsupdate(fn, tsig_key_file)


"""Dynamically delete a PTR record.

    :param server_ip: the IP address of the DNS server on which to delete the record.
    :param reverse_name: the reverse space name of the record to delete.
    :param tsig_key_file: the name of the optional TSIG key file to use.

"""


def delete_ptr(server_ip, reverse_name, tsig_key_file=None):
    fn = os.tmpnam()
    f = open(fn, 'w')
    f.write('server %s\n' % server_ip)
    f.write('update delete %s ptr\n' % reverse_name)
    f.write('send\n')
    f.close()
    run_nsupdate(fn, tsig_key_file)
