#!/usr/bin/env python
import sys, os, datetime, json, base64, socket

sys.path.append("/opt/splunk/etc/apps/framework/contrib/splunk-sdk-python/")
import splunklib.client as client
import splunklib.results as results

from time import sleep
from bluecat import api
from bluecat import api_exception
from bluecat import entity
from bluecat.wrappers import generic_getters
from AppConfig import AppConfig

## FUNCTIONS ##
def checkConnection():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((BAMIP, 6667))

    if result == 0:
        # Port is open
        return 1
    else:
        # Port is unreachable
        return 0


def getObjectId(objType, objName):
    bam = api('http://' + BAMIP + '/Services/API?wsdl')
    bam.login(APIUSER, APIPASS)

    if objType == "Configuration":
        obj = bam._soap_client.service.getEntityByName(0, objName, "Configuration")
        return obj['id']

    if objType == "ResponsePolicy":
        obj = bam._soap_client.service.getEntityByName(OBJID_BAMCONFIG, objName, "ResponsePolicy")
        return obj['id']

    if objType == "Server":
        objArr = []
        for name in objName:
            obj = bam._soap_client.service.getEntityByName(OBJID_BAMCONFIG, name, "Server")
            objArr.append(int(obj['id']))
        return objArr

def block_tunnel(maldomain):
    # Talk to BlueCat Address Manager
    api_url = 'http://' + BAMIP + '/Services/API?wsdl'
    bam = api(api_url)
    bam.login(APIUSER, APIPASS)

    #conf = bam.get_configuration('ACME Corp')

    tg = bam._soap_client.service.getEntityByName(0, TAG_TUNNEL, "TagGroup")
    if tg.id==0:
        tg = bam._soap_client.service.addTagGroup(TAG_TUNNEL, "")

    try:
        bam._soap_client.service.addTag(tg.id, "**." + maldomain, "")
        e = bam._soap_client.service.getEntities(tg.id, "Tag", 0, 1000)
        blacklistItems = ''
        for entity in e.item:
            blacklistItems += '\n' + entity.name
        bam._soap_client.service.uploadResponsePolicyItems(OBJID_RPZ, base64.b64encode(blacklistItems))

        for dds in OBJID_DDS:
            bam._soap_client.service.deployServerConfig(dds, "services=DNS|forceDNSFullDeployment=true")
        return 0
    except:
        return 1

def log(msg):
    f = open(os.path.join(os.environ["SPLUNK_HOME"], "var", "log", "splunk", "bluecat_dns_alert.log"), "a")
    print >> f, str(datetime.datetime.now().isoformat())+ ',' +msg
    f.close()

###########################################################

## Splunk App configuration file, use default if not set
configFile = AppConfig()

BAMIP = configFile.get_BamIP()
print BAMIP
APIUSER = configFile.get_BamApiUsername()
print APIUSER
APIPASS = configFile.get_BamApiPassword()

if BAMIP in [None, '127.0.0.1']:
    OBJID_BAMCONFIG = 0

    TAG_TUNNEL = 'splunk_dnstunnel_blacklist'
    OBJID_RPZ = 0
    OBJID_DDS = ''

    TUN_DETECT_LENGTH = 35
    TUN_COUNT_PER_INT = 8

    ALERT = 0
    BLOCK = 0

else:
    if checkConnection() == 1:

        if configFile.get_BamConfigId() == 0:
            OBJID_BAMCONFIG = getObjectId("Configuration", configFile.get_Configuration())
            configFile.set_BamConfigId(OBJID_BAMCONFIG)
        else:
            OBJID_BAMCONFIG = configFile.get_BamConfigId()

        if configFile.get_RpzId() == 0:
            OBJID_RPZ = getObjectId("ResponsePolicy", configFile.get_ResponsePolicy())
            configFile.set_RpzId(OBJID_RPZ)
        else:
            OBJID_RPZ = configFile.get_RpzId()

        if configFile.get_DdsId() == 0:
            OBJID_DDS = getObjectId("Server", configFile.get_DDSNames())
            configFile.set_DdsId(OBJID_DDS)
        else:
            OBJID_DDS = configFile.get_DdsId()

        TAG_TUNNEL = 'splunk_dnstunnel_blacklist'

        ## DNS Tunnel Detection
        TUN_DETECT_LENGTH = str(configFile.get_QueryLength())
        TUN_COUNT_PER_INT = str(configFile.get_QueryRate())

        ## Mitigation and Response
        actionType = configFile.get_Action()
        ALERT = actionType[0]
        BLOCK = actionType[1]

        ## Default Splunk Settings
        HOST = "localhost"
        PORT = 8089
        USERNAME = "admin"
        PASSWORD = "changeme"
        exec_mode = {"earliest_time" : "-30s", "latest_time" : "now", "count" : 0}

        # This search checks based on DNS Query (requires querylogging)
        #entropy_search = "search index=bluecatindex sourcetype="bluecat:dns:query" | eval length=len(dnsquery) | search length > 50 | rex field=dnsquery "\.(?P<FQDN>\w+\.\w.+\.\w.+)$" | stats count by FQDN, dnsclient | search count > 8 | sort - count"

        # This search checks based on Rate Limit Hit (Rate Limit is required, optional QueryLogging)
        entropy_search = "search index=bluecatindex sourcetype=\"bluecat:dns:rate\" | eval length=len(dnsquery) | search length > " + TUN_DETECT_LENGTH + " | stats count by dnsfqdn, dnsclient | search count > " + TUN_COUNT_PER_INT

        # Create a Splunk Search Service instance and log in
        service = client.connect(host=HOST, port=PORT, username=USERNAME, password=PASSWORD)

        search_results = service.jobs.oneshot (entropy_search, **exec_mode);
        for item in results.ResultsReader(search_results):
            logstr = item['dnsfqdn'] + ',' + item['dnsclient'] + ',' + item['count']
            log(logstr + ',DETECTED')

            if ALERT:
                print "<ALERT> DNS Tunneling detect: " + logstr

            if BLOCK:
                print "<BLOCKED> DNS Tunneling detect and blocked: " + logstr
                if block_tunnel(item['dnsfqdn']) == 1:
                    log (logstr + ',BLOCKED')
                else:
                    log (logstr + ',NOTBLOCKED')
