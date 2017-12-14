#!/usr/bin/env python
import sys, os, datetime, json, base64

from time import sleep
from bluecat import api
from bluecat import api_exception
from bluecat import entity
from bluecat.wrappers import generic_getters
from AppConfig import AppConfig

configFile = AppConfig()

BAMIP = configFile.get_BamIP()
APIUSER = configFile.get_BamApiUsername()
APIPASS = configFile.get_BamApiPassword()

BAMCONFIG = configFile.get_Configuration()

TAG_TUNNEL = 'splunk_dnstunnel_blacklist'

RPZPOLICY = configFile.get_ResponsePolicy()
DDSNAMES = configFile.get_DDSNames()

## DNS Tunnel Detection
## 1. Length = Minimum: 35
## 2. Count per Interval = Minimum: 8
TUN_DETECT_LENGTH = configFile.get_QueryLength()
TUN_COUNT_PER_INT = configFile.get_QueryRate()

## Mitigation and Response
actionType = configFile.get_Action()
ALERT = actionType[0]
BLOCK = actionType[1]

# Talk to BlueCat Address Manager
bam = api('http://' + BAMIP + '/Services/API?wsdl')
bam.login(APIUSER, APIPASS)

bamConfig = bam._soap_client.service.getEntityByName(0, BAMCONFIG, "Configuration")
OBJID_BAMCONFIG = bamConfig['id']
print OBJID_BAMCONFIG

rpzPolicy = bam._soap_client.service.getEntityByName(OBJID_BAMCONFIG, RPZPOLICY, "ResponsePolicy")
OBJID_RPZPOLICY = rpzPolicy['id']
print OBJID_RPZPOLICY

ddsID = []
for dds in DDSNAMES:
    ddsName = bam._soap_client.service.getEntityByName(OBJID_BAMCONFIG, dds, "Server")
    ddsID.append(int(ddsName['id']))

OBJID_DDSNAMES = ddsID
print OBJID_DDSNAMES
