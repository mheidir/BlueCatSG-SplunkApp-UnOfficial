from suds import WebFault

from entity import entity
from util import *


class server(entity):
    """Server objects.
    """

    DNS = 'DNS'
    DHCP = 'DHCP'
    DHCPv6 = 'DHCPv6'
    TFTP = 'TFTP'

    def __init__(self, api, soap_entity, soap_client):
        super(server, self).__init__(api, soap_entity, soap_client)

    def deploy(self):
        """Deploy a server.
        """
        try:
            self._soap_client.service.deployServer(self.get_id())
        except WebFault as e:
            raise api_exception(e.message)

    def deploy_services(self, services=['DNS', 'DHCP', 'DHCPv6', 'TFTP'], force_full_dns=False):
        """Deploy specific services to a server.

        :param services: List of services to deploy.
        :param force_full_dns: Force a full deployment if true. Note that this actually means just send the full data to the server.
            What happens to the service itself will depend on whether or not its running at the time.
        """
        try:
            properties = 'services=' + ','.join(services)
            if force_full_dns:
                properties += '|forceDNSFullDeployment=true'
            self._soap_client.service.deployServerServices(self.get_id(), properties)
        except WebFault as e:
            raise api_exception(e.message)

    def get_service_ip4_addresses(self):
        """Get the list of service IP4 addresses.
        """
        res = []
        for i in self.get_children_of_type('NetworkServerInterface'):
            if 'servicesIPv4Address' in i.get_properties():
                res.append(i.get_properties()['servicesIPv4Address'])
        return res

    def get_service_ip6_addresses(self):
        """Get the list of service IP6 addresses.
        """
        return []

    def run_clish(self, commands):
        """Run a list of commands on the server using clish. For this work an SSH key pair for root allowing login without
           The need to enter a password must have been setup.

        :param commands: String of clish commands with embedded linefeeds.
        """
        ip = self.get_property('defaultInterfaceAddress')
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(commands)
        f.close()
        command_file_name = "command%s.clish" % random.randint(0, 1000000000)
        os.system('scp %s root@%s:%s' % (f.name, ip, command_file_name))
        os.system("ssh root@%s '/root/run-clish.sh %s > %s.txt 2>&1'" % (ip, command_file_name, command_file_name))
        os.system('scp root@%s:%s.txt %s' % (ip, command_file_name, f.name))
        os.system("ssh root@%s 'rm -f %s %s.txt'" % (ip, command_file_name, command_file_name))
        f = open(f.name)
        res = f.read().split('\n')
        f.close()
        os.unlink(f.name)
        return res

    def set_ssh_credentials(self, username='', password=''):
        """Set the username and password for SSH connections

        :param username: Login to SSH with this username.
        :param password: Login to SSh with this password.
        """
        self._sshuser = username
        self._sshpass = password

    def run_psmclient(self, command, timeout=30):
        """Execute a PsmClient command on the server

        The username and password must be set with set_ssh_credentials, if shared key authentication is not configured.
        :param commands: String containing PsmClient command to execute.
        :return: Returns the output from the command executed.
        """
        ip = self.get_property('defaultInterfaceAddress')
        cmd = '/usr/local/bluecat/PsmClient ' + command
        output, error = run_ssh_cmd(ip, self._sshuser, self._sshpass, cmd, timeout)
        if 'retcode=ok' in output:
            return output
        else:
            return output + error

    def get_static_routes(self):
        """Get a dictionary of static routes for a server.

        The return value is a dictionary of route IDs to [network address, mask, gateway] arrays.
        """
        commands = 'configure static-routes\nshow\n'
        result = {}
        for l in self.run_clish(commands):
            i = l.find('Network=')
            if i != -1:
                bits = l.split(',')
                if len(bits) > 2:
                    key = int(bits[0].strip().split('.')[0])
                    result[key] = [bits[0].strip().split('=')[1], bits[1].strip().split('=')[1],
                                   bits[2].strip().split('=')[1]]
        return result

    def update_static_routes(self, routes):
        """Update static routes for a server.

        :param routes: a dictionary of route IDs to [network address, mask, gateway] arrays.
        """
        current_routes = set()
        new_routes = set()
        for r in self.get_static_routes().values():
            current_routes.add(tuple(r))
        for r in routes:
            new_routes.add((str(r['network']), str(r['mask']), str(r['via'])))
        to_add = new_routes.difference(current_routes)
        to_delete = current_routes.difference(new_routes)
        try:
            self.add_static_routes(to_add)
        except api_exception as e:
            # if anything went wrong, undo whatever we did
            try:
                self.delete_static_routes(to_add)
            except:
                pass
            raise e
        self.delete_static_routes(to_delete)

    def add_static_routes(self, routes):
        """Add a list of static routes.

        :param routes: a list of [network address, mask, gateway] arrays.
        """
        # these are done individually so as to allow the specific route with an error to be identified in case of trouble
        for r in routes:
            commands = 'configure static-routes\n'
            commands += 'add route network %s mask %s via-address %s\n' % r
            commands += 'save\n'
            for l in self.run_clish(commands):
                if l.find('Invalid') != -1:
                    raise api_exception('route %s mask %s via %s is invalid.' % r)

    def delete_static_routes(self, routes):
        """Delete a list of static routes.

        :param routes: a list of [network address, mask, gateway] arrays.
        """
        for r in routes:
            commands = 'configure static-routes\n'
            commands += 'remove route network %s mask %s via-address %s\n' % r
            commands += 'save\n'
            self.run_clish(commands)

    def add_nameserver_addresses(self, addrs):
        """Add a list of nameserver addresses.

        :param addrs: a list of nameserver IPs addresses (as strings).
        """
        for a in addrs:
            commands = 'configure name-server\n'
            commands += 'add address %s\n' % a
            commands += 'save\n'
            for l in self.run_clish(commands):
                if l.find('Invalid') != -1:
                    raise api_exception('address %s is invalid.' % a)

    def delete_nameserver_addresses(self, addrs):
        """Delete a list of nameserver addresses.

        :param addrs: a list of nameserver IPs addresses (as strings).
        """
        for a in addrs:
            commands = 'configure name-server\n'
            commands += 'remove address %s\n' % a
            commands += 'save\n'
            for l in self.run_clish(commands):
                if l.find('Invalid') != -1:
                    raise api_exception('address %s is invalid.' % a)

    def add_nameserver_domain_names(self, names):
        """Add a list of nameserver domain names.

        :param addrs: a list of nameserver domain names.
        """
        for n in names:
            commands = 'configure name-server\n'
            commands += 'add domain-name %s\n' % n
            commands += 'save\n'
            for l in self.run_clish(commands):
                if l.find('Invalid') != -1:
                    raise api_exception('domain name %s is invalid.' % n)

    def delete_nameserver_domain_names(self, names):
        """Delete a list of nameserver domain names.
        :param addrs: a list of nameserver domain names.
        """
        for n in names:
            commands = 'configure name-server\n'
            commands += 'remove domain-name %s\n' % n
            commands += 'save\n'
            for l in self.run_clish(commands):
                if l.find('Invalid') != -1:
                    raise api_exception('domain name %s is invalid.' % n)

    def add_nameserver_search_domains(self, domains):
        """Add a list of nameserver search domains.

        :param addrs: a list of nameserver search domains.
        """
        for sd in domains:
            commands = 'configure name-server\n'
            commands += 'add search-domain %s\n' % sd
            commands += 'save\n'
            for l in self.run_clish(commands):
                if l.find('Invalid') != -1:
                    raise api_exception('search domain server %s is invalid.' % sd)

    def delete_nameserver_search_domains(self, domains):
        """Delete a list of nameserver search domains.

        :param addrs: a list of nameserver search domains.
        """
        for sd in domains:
            commands = 'configure name-server\n'
            commands += 'remove search-domain %s\n' % sd
            commands += 'save\n'
            for l in self.run_clish(commands):
                if l.find('Invalid') != -1:
                    raise api_exception('search domain %s is invalid.' % sd)

    def get_nameservers(self):
        """Get a tuple of (addresses, domain names and search domains) for nameservers.
        """
        commands = 'configure name-server\nshow\n'
        addresses = []
        domain_names = []
        search_domains = []
        state = None
        for l in self.run_clish(commands):
            if l.strip() != '':
                if l.find('Name Servers:') != -1:
                    state = "addresses"
                elif l.find('Domain Names:') != -1:
                    state = "domain_names"
                elif l.find('Search Domains:') != -1:
                    state = "search_domains"
                elif state == "addresses":
                    addresses.append(l.split('=')[1].strip())
                elif state == "domain_names":
                    domain_names.append(l.split('=')[1].strip())
                elif state == "search_domains":
                    search_domains.append(l.split('=')[1].strip())
        return addresses, domain_names, search_domains

    def update_nameservers(self, addresses, domain_names, search_domains):
        """ Update addresses, domain names and search domains for nameservers.
        """
        current_addresses, current_domain_names, current_search_domains = self.get_nameservers()
        s1 = set(current_addresses)
        s2 = set(addresses)
        to_add = s2.difference(s1)
        to_delete = s1.difference(s2)
        try:
            self.add_nameserver_addresses(to_add)
        except api_exception as e:
            # if anything went wrong, undo whatever we did
            try:
                self.delete_nameserver_addresses(to_add)
            except:
                pass
            raise e
        self.delete_nameserver_addresses(to_delete)
        s1 = set(current_domain_names)
        s2 = set(domain_names)
        to_add = s2.difference(s1)
        to_delete = s1.difference(s2)
        try:
            self.add_nameserver_domain_names(to_add)
        except api_exception as e:
            # if anything went wrong, undo whatever we did
            try:
                self.delete_nameserver_domain_names(to_add)
            except:
                pass
            raise e
        self.delete_nameserver_domain_names(to_delete)
        s1 = set(current_search_domains)
        s2 = set(search_domains)
        to_add = s2.difference(s1)
        to_delete = s1.difference(s2)
        try:
            self.add_nameserver_search_domains(to_add)
        except api_exception as e:
            # if anything went wrong, undo whatever we did
            try:
                self.delete_nameserver_search_domains(to_add)
            except:
                pass
            raise e
        self.delete_nameserver_search_domains(to_delete)
