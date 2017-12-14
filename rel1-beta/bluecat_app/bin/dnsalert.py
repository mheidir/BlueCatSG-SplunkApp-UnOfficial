#!/usr/bin/env python
import sys, os, datetime
sys.path.append("/opt/splunk/etc/apps/framework/contrib/splunk-sdk-python/")

from time import sleep
import splunklib.client as client
import splunklib.results as results
from bluecat import api
from bluecat import api_exception
from bluecat import entity
from bluecat.wrappers import generic_getters
import json
import base64

def block_tunnel(malware):
        # Talk to BlueCat Address Manager
        api_url = 'http://10.0.1.251/Services/API?wsdl'
        bam = api(api_url)
        bam.login('apiuser', 'bluecat')

        #conf = bam.get_configuration('ACME Corp')

        tg = bam._soap_client.service.getEntityByName(0, "dnstunnel-malware", "TagGroup")
        if tg.id==0:
                tg = bam._soap_client.service.addTagGroup('dnstunnel-malware', "")

        try:
                bam._soap_client.service.addTag(tg.id, "**." + malware, "")
                e = bam._soap_client.service.getEntities(tg.id, "Tag", 0, 1000)
                blacklistItems = ''
                for entity in e.item:
                        blacklistItems += '\n' + entity.name
                bam._soap_client.service.uploadResponsePolicyItems(1651093, base64.b64encode(blacklistItems))
		bam._soap_client.service.deployServerConfig(140183, "services=DNS|forceDNSFullDeployment=true")
		return 0
        except:
		return 1


def log(msg):
    f = open(os.path.join(os.environ["SPLUNK_HOME"], "var", "log", "splunk", "bluecat_dns_alert.log"), "a")
    print >> f, str(datetime.datetime.now().isoformat())+ ',' +msg
    f.close()


HOST = "localhost"
PORT = 8089
USERNAME = "admin"
PASSWORD = "changeme"
exec_mode = {"earliest_time" : "-30s", "latest_time" : "now", "count" : 0}
entropy_search = "search named rate limit | eval length=len(rateName) | search length > 40 | stats count by rateDomain, rateClientIP | search count > 8"

# Create a Service instance and log in
service = client.connect(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD)

search_results = service.jobs.oneshot (entropy_search, **exec_mode);
for item in results.ResultsReader(search_results):
	logstr = item['rateDomain'] + ',' + item['rateClientIP'] + ',' + item['count']
	tempstr = logstr + ',DETECTED'
	log (tempstr)
	if block_tunnel(item['rateDomain']) == 1:
		logstr += ",BLOCKED"
		log (logstr)
