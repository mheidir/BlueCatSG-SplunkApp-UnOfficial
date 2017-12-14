# PATCH 1.5.5 - 
#	Logs an error when IP exhaustion happens
#	Logs a debug message for OSPF anycast IP setting

import os

from bluecat import api
from bluecat import api_exception
from bluecat import entity
from bluecat.wrappers import generic_getters

from pysnmp.hlapi import *
from urllib2 import URLError
import time
import socket, struct

def len_to_mask (ml):
	cidr = 0	
	if int(ml) <= 32: 
		mask = (1<<32) - (1<<32>>int(ml))
		cidr = socket.inet_ntoa(struct.pack(">L", mask))
	return cidr 

class bam:

	global _shared_state
	_shared_state = {}
	_shared_state["logger"] = None 

    	def __init__(self, ip=None, user="apiuser", password="bluecat", conf='zte', logger=None):
		self._identity = _shared_state

		if "connstate" in self._identity and self._identity["connstate"] == 1:
			return;
		else:
			if ip != None:
				self._identity["ip"] = ip
				self._identity["user"] = user
				self._identity["password"] = password 
				self._identity["api_url"] = 'http://' + str(ip) + '/Services/API?wsdl'
				self._identity["logger"] = logger
				self._identity["conf"] = conf
				self._identity["view"] = "recursive"
				self._identity["taggroup"] = "vBDDS"
				self._identity["connstate"] = 0
			else:
				if self._identity["ip"] == None:
					return 0;

	def get_block(self, net, blkname):
		if net is "":
        		blk = generic_getters.get_entity_by_name(self.api._soap_client, self.conf.get_id(), blkname, "IP4Block")
        		if blk.id != 0:
            			return self.api.get_entity_by_id(blk.id)
        		return 0
		else:
        		blk = generic_getters.get_entity_by_name(self.api._soap_client, self.conf.get_id(), blkname, "IP4Block")
        		if blk.id != 0:
            			return self.api.get_entity_by_id(blk.id)
        		return self.conf.add_ip4_block_by_cidr(net, "name="+blkname)

	def get_network(self, blk, net, netname):
        	netObj = generic_getters.get_entity_by_name(self.api._soap_client, blk.get_id(), netname, "IP4Network")
        	if netObj.id != 0:
            		return self.api.get_entity_by_id(netObj.id)
        	else:
			if net is "":
				return 0
            		else:
            			return blk.add_ip4_network(net, "name="+netname)

	def init_bam(self, params=None):
		user = self._identity["user"]
		password = self._identity["password"]
		conf = self._identity["conf"]
		logger = self._identity["logger"]
		viewname = self._identity["view"]
		taggroupname = self._identity["taggroup"]

		api_url = self._identity["api_url"]

		try:
			self.api = api(self._identity["api_url"])
        	except URLError, e:
                	logger.error ("FAILED TO CONNECT TO BAM: " + api_url + "(" + str(e.args) +")" )
			return 1;

		try:
			self.api.login(user, password)
        	except api_exception as e:
                	logger.error ("FAILED TO LOGIN TO BAM: " + api_url)
			return 1;

		try:
			self.conf = self.api.get_configuration(conf)
        	except api_exception as e:
                	logger.error ("FAILED TO ACCESS CONFIGURATION zte ON BAM")
			return 1;
			
		self._identity["connstate"] = 1
		logger.debug("SUCCESSFULY CONNECTED TO BAM and accessed configuration:" +  self.conf.get_name() )

		if params is not None and "service_net" in params:
        		self.service_blk = self.get_block(params["service_net"], "Service Block")
		else:
        		self.service_blk = self.get_block("", "Service Block")

        	logger.debug ("service blk is " + str(self.service_blk.get_id()))

		if params is not None and "mgmt_net" in params:
        		self.mgmt_blk = self.get_block(params["mgmt_net"], "Management Block")
		else:
        		self.mgmt_blk = self.get_block("", "Management Block")
        	logger.debug ("mgmt blk is " + str(self.mgmt_blk.get_id()))

		if params is not None and "service_net" in params:
        		self.service_net = self.get_network(self.service_blk, params["service_net"], "Service Network")
		else:
        		self.service_net = self.get_network(self.service_blk, "", "Service Network")
        	logger.debug ("service net is " + str(self.service_net.get_id()))
		
		if params is not None and "mgmt_net" in params:
        		self.mgmt_net = self.get_network(self.mgmt_blk, params["mgmt_net"], "Management Network")
		else:
        		self.mgmt_net = self.get_network(self.mgmt_blk, "", "Management Network")
        	logger.debug ("mgmt net is " + str(self.mgmt_net.get_id()))

        	self.view = self.conf.get_view(viewname)
        	if self.view.get_id() == 0:
           		self.view = self.conf.add_view(viewname)
        	logger.debug ("view id is " + str(self.view.get_id()))

        	tagGroup = generic_getters.get_entity_by_name(self.api._soap_client, 0, taggroupname, "TagGroup")
        	if tagGroup.id == 0:
                	self.tagGroup = self.api._soap_client.service.addTagGroup(taggroupname, "")
        	else:
                	self.tagGroup = tagGroup.id

        	logger.debug ("taggroup id is " + str(self.tagGroup))

    	def reserve_server(self, mgmt_props, dns_props):
		logger = self._identity["logger"]
        	mgmt_subnet = self.mgmt_net._properties["CIDR"].split("/")[1]
        	service_subnet = self.service_net._properties["CIDR"].split("/")[1]

		# Assign the next available IP on the Management Network
		m_ip_id = 0
		if mgmt_props == "":
        		mgmt_ip = self.api._soap_client.service.assignNextAvailableIP4Address(self.conf.get_id(), self.mgmt_net.get_id(), "", "", "MAKE_RESERVED", "")
        		m_ip = self.api.instantiate_entity(mgmt_ip, self.api._soap_client)
        		vdu_m_ip = m_ip._properties['address']
			m_ip_id = m_ip.get_id()
		else:
        		m_ip = self.api._soap_client.service.getNextIP4Address(self.mgmt_net.get_id(), mgmt_props)
			if m_ip == None:
				logger.error ("Management Network - IP addresses exhausted")

        		m_ip_id = self.api._soap_client.service.assignIP4Address(self.conf.get_id(), m_ip, "", "", "MAKE_RESERVED", "")
        		vdu_m_ip = m_ip
			

		# Assign the next available IP on the Service Network
		if dns_props == "":
        		service_ip = self.api._soap_client.service.assignNextAvailableIP4Address(self.conf.get_id(), self.service_net.get_id(), "", "", "MAKE_RESERVED", "")
        		s_ip = self.api.instantiate_entity(service_ip, self.api._soap_client)
        		vdu_s_ip = s_ip._properties['address']
			s_ip_id = s_ip.get_id()
		else:
        		service_ip = self.api._soap_client.service.getNextIP4Address(self.service_net.get_id(), dns_props)
			if service_ip == None:
				logger.error ("Service Network - IP addresses exhausted")

			s_ip_id = self.api._soap_client.service.assignIP4Address(self.conf.get_id(), service_ip, "", "", "MAKE_RESERVED", "")
        		vdu_s_ip = service_ip

        	servername = "vBDDS-" + str(m_ip_id)
        	try:
                	server_tag = self.api._soap_client.service.addTag(self.tagGroup, servername, "")
                	self.api._soap_client.service.linkEntities(server_tag, s_ip_id)
        	except api_exception as e:
                	logger.debug ("failed to add server tag for " + servername)

        	vdu = { "entityid" : m_ip_id, "m_ip": vdu_m_ip + "/" + mgmt_subnet, "s_ip": vdu_s_ip + "/" + service_subnet}
        	return vdu

	def get_service_ip_for_server (self, servername):
		logger = self._identity["logger"]
		sip = 0;
		sipitem = None
               	server_tag = generic_getters.get_entity_by_name(self.api._soap_client, self.tagGroup, servername, "Tag")
               	logger.debug ("get_service_ip_for_server: " + servername + ": found server tag: " + str(server_tag.id))
               	if server_tag.id != 0:
                       	ip = self.api._soap_client.service.getLinkedEntities(server_tag.id, "IP4Address", 0, 1)
                       	for item in ip[0]:
				sipitem = item
                               	temp = item["properties"]
                               	sip = (temp.split('address=')[1]).split('|')[0]

		return sipitem, sip, server_tag.id
	
	def add_server(self, servername, service_ip):
		logger = self._identity["logger"]
		logger.debug ("Called add server :" + servername)

        	id = servername.split("-")[1]
		masklen = 24

		try:
        		ip_obj = self.api.get_entity_by_id(id)
		except api_exception as e:
			logger.error (e)
			return;

        	ipaddress = ip_obj._properties['address']

		logger.debug ("Got IP address : " + str(ipaddress) + " for server : " + servername)
		
		try:
        		server_obj = self.conf.get_server(servername)
		except api_exception as e:
			logger.error (e)
			return;

        	if service_ip == "":
			sipitem, sip, stag = self.get_service_ip_for_server(servername)
        	else:
                	sip = service_ip.split('/')[0]
			masklen = service_ip.split('/')[1]
     
		netmask = len_to_mask(masklen)
 
		# Start adding the server  
		logger.debug ("Starting timer to add server " + servername + ' with management ip='+ str(ipaddress) + ' and serviceip=' + str(sip) + "/" + str(netmask))
        	if server_obj is None:
                	retry = 0
                	while retry < 100:
                        	try:
                                	server_obj = self.conf.add_server(servername, ipaddress, servername, "password=bluecat|connected=true|servicesIPv4Address="+str(sip) +
                                	"|servicesIPv4Netmask=" + str(netmask))
                                	retry = 100
                        	except api_exception as e:
                                	logger.debug (str(e))
                                	server_obj = self.conf.get_server(servername)
                                	if server_obj != None:
                                        	retry = 100
                                	else:
                                        	retry = retry + 1
                                        	time.sleep(10)
                                        	if retry > 20:
                                                	retry = 100
                        	except socket.timeout:
                                	logger.debug ("Almost done in add_server..")

		# Deploy DNS
        	server_intf = generic_getters.get_entity_by_name(self.api._soap_client, server_obj.get_id(), servername, "NetworkServerInterface")
        	dnsdeploy = self.api._soap_client.service.getDNSDeploymentRole(self.view.get_id(), server_intf.id)
        	if dnsdeploy.id == 0:
                	dnsdeploy = self.api._soap_client.service.addDNSDeploymentRole(self.view.get_id(), server_intf.id, "RECURSION", "view="+self.view.get_name())

        	status = self.api._soap_client.service.getServerDeploymentStatus(server_obj.get_id(), "")
        	if status in [3,4,5,6,7,8]:
                	self.api._soap_client.service.deployServer(server_obj.get_id())

        	return server_obj

	def del_server(self, servername):
		logger = self._identity["logger"]
        	server = self.conf.get_server(servername)
        	if server is not None:
            		server_id = server.get_id()
            		self.api._soap_client.service.delete(server_id)

		# Release the Management IP
        	ip_id = servername.split("-")[1]
        	try:
            		ip_obj = self.api.get_entity_by_id(ip_id)
            		self.api._soap_client.service.delete(ip_obj.get_id())
        	except:
            		logger.debug("No IP found")

		# Release the Service IP
        	try:
			sipitem, sip, stag = self.get_service_ip_for_server(servername)
			if sip != 0:
                       		self.api._soap_client.service.delete(sipitem["id"])
			if stag != 0:
                		self.api._soap_client.service.delete(stag)
        	except api_exception as e:
            		logger.debug ("Failed to release tag and service ip for " + servername + " exception: " + e)

	def wait_for_deployment(self, server, dyn_params):
		logger = self._identity["logger"]
        	sid = server.get_id()
        	status = self.api._soap_client.service.getServerDeploymentStatus(sid)
        	counter = 1
        	while status not in [6,7,8]:
            		time.sleep(2)
            		counter += 1
            		if counter > 5:
               			break
            		status = self.api._soap_client.service.getServerDeploymentStatus(sid)

        	server.set_ssh_credentials ('root', 'd8e8fca')

		# Add SNMP enable here
                cmd = 'node set snmp-enable=1'
                server.run_psmclient (cmd)
		
        	# Add anycast settings here
        	if dyn_params['anycast_ip']:
                	cmd = 'anycast set anycast-ipv4=' + dyn_params['anycast_ip'] + ' component=common vtysh-enable=1'
                	logger.debug ('Setting anycast : ' + cmd)
                	server.run_psmclient (cmd)

        	if dyn_params['anycast_protocol'] == 'ospfd':
                	cmd = ( 'anycast set area=' + dyn_params['ospf_area'] + ' authenticate='
                 	+ dyn_params['ospf_authenticate'] + ' component=ospfd dead-interval=' + dyn_params['ospf_dead_interval']
                 	+ ' enabled=1 hello-interval=' + dyn_params['ospf_hello_interval'] + ' password=' + dyn_params['ospf_password']
                 	+ ' stub=' + dyn_params['ospf_stub'] )
                	logger.debug ('Setting OSPF : ' + cmd)
                	server.run_psmclient (cmd)

                	cmd = 'node set anycast-enable=1'
                	server.run_psmclient (cmd)

	def snmp_get_lowest(self, oid):
        	val = 0;
        	singleVal = 0;
        	for s in self.conf.get_servers():
            		id = s.get_name().split("-")[1]
            		ip_obj = self.api.get_entity_by_id(id)
            		ipaddress = ip_obj._properties['address']
           		print "Getting SNMP params from server " + str(ipaddress)
           		errorIndication, errorStatus, errorIndex, varBinds = next(
                		getCmd(SnmpEngine(),
                		CommunityData("ztetest"),
                		UdpTransportTarget((ipaddress, 161)),
                		ContextData(),
                		ObjectType(ObjectIdentity(oid))
                		)
            		)

            		if errorIndication:
                		print errorIndication
                		singleVal = 0
            		elif errorStatus:
                		print errorStatus
                		singleVal = 0
            		else:
                		print varBinds[0][1]
                		singleVal = varBinds[0][1]
                		if singleVal < val:
                    			val = singleVal
        	return val

	def snmp_get_highest(self, oid):
        	val = 0;
        	singleVal = 0;
        	for s in self.conf.get_servers():
            		id = s.get_name().split("-")[1]
            		ip_obj = self.api.get_entity_by_id(id)
            		ipaddress = ip_obj._properties['address']
            		print "Getting SNMP params from server " + str(ipaddress)
            		errorIndication, errorStatus, errorIndex, varBinds = next(
                		getCmd(SnmpEngine(),
                		CommunityData("ztetest"),
                		UdpTransportTarget((ipaddress, 161)),
                		ContextData(),
                		ObjectType(ObjectIdentity(oid))
                		)
            		)
            		if errorIndication:
                		print errorIndication
                		singleVal = 0
            		elif errorStatus:
                		print errorStatus
                		singleVal = 0
           		else:
                		print varBinds[0][1]
                		singleVal = varBinds[0][1]

            		if singleVal >= 100:
                		singleVal = 99

            		if singleVal > val:
                		val = singleVal
        	return val

