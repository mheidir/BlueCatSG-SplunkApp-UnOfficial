#!/usr/bin/env python
#
# Reference:
# https://stackoverflow.com/questions/8774830/how-with-is-better-than-try-catch-to-open-a-file-in-python
# https://dbader.org/blog/python-check-if-file-exists
# https://stackoverflow.com/questions/4843158/check-if-a-python-list-item-contains-a-string-inside-another-string
# http://pythoncentral.io/cutting-and-slicing-strings-in-python/
# https://stackoverflow.com/questions/53513/best-way-to-check-if-a-list-is-empty
# https://stackoverflow.com/questions/4071396/split-by-comma-and-strip-whitespace-in-python
# https://stackoverflow.com/questions/10487278/how-to-declare-and-add-items-to-an-array-in-python

import os

class AppConfig:
    DEFAULTFILE = os.path.join(os.environ["SPLUNK_HOME"], "etc", "apps", "bluecat_app", "default", "bluecat.conf")
    LOCALFILE = os.path.join(os.environ["SPLUNK_HOME"], "etc", "apps", "bluecat_app", "local", "bluecat.conf")

    configId = 0
    rpzId = 0
    ddsId = 0

    def __init__(self):
        if (os.path.isfile(self.LOCALFILE)):
            self.fileinput = self.open_ConfigFile(self.LOCALFILE)
        else:
            print "Application config file does not exists. Using default config file from package"
            self.fileinput = self.open_ConfigFile(self.DEFAULTFILE)

    # FUNCTIONS
    def open_ConfigFile(self, filename):
        with open(filename, 'r') as f:
            lines = f.read().splitlines()

            return lines

    def write_ObjId(self, objName, objId):
        if (os.path.isfile(self.LOCALFILE)):
            fh = open(self.LOCALFILE, "a")
            fh.write(objName + " = " + objId)
            fh.close

    def get_BamConfigId(self):
        configid = self.searchMatch("configid", self.fileinput)

        idx = 0
        if configid:
            strconfigid = configid[0]
            idx = strconfigid[11:]

        self.configId = idx
        return idx

    def set_BamConfigId(self, objId):
        if (os.path.isfile(self.LOCALFILE)):
            self.write_ObjId("configid", objId)

    def get_RpzId(self):
        rpzid = self.searchMatch("rpzid", self.fileinput)

        idx = 0
        if rpzid:
            strrpzid = rpzid[0]
            idx = strrpzid[8:]

        self.rpzId = idx
        return idx

    def set_RpzId(self, objId):
        if (os.path.isfile(self.LOCALFILE)):
            self.write_ObjId("rpzid", objId)

    def get_DdsId(self):
        ddsid = self.searchMatch("ddsid", self.fileinput)

        idx = 0
        if ddsid:
            strddsid = ddsid[0]
            idx = strddsid[8:]

        self.ddsId = idx
        return idx

    def set_DdsId(self, objId):
        if (os.path.isfile(self.LOCALFILE)):
            self.write_ObjId("ddsid", objId)

    def get_BamIP(self):
        bamip = self.searchMatch("bamip", self.fileinput)

        ip = ""
        if bamip:
            strbamip = bamip[0]
            #bamip = 10.0.1.252
            ip = strbamip[8:]

        return ip

    def get_Configuration(self):
        bamconfig = self.searchMatch("configuration", self.fileinput)

        config = ""
        if bamconfig:
            strbamconfig = bamconfig[0]
            #configuration = ACME Corp
            config = strbamconfig[16:]

        return config

    def get_ResponsePolicy(self):
        responsepolicy = self.searchMatch("responsepolicy", self.fileinput)

        policy = ""
        if responsepolicy:
            strresponsepolicy = responsepolicy[0]
            #responsepolicy = splunk_dnstunnel_blacklist
            policy = strresponsepolicy[17:]

        return policy

    def get_DDSNames(self):
        ddsnames = self.searchMatch("ddsnames", self.fileinput)

        ddslist = []
        if ddsnames:
            names = ddsnames[0]
            strnames = names[11:]
            #ddsnames = dds1, dds2
            # Return array containing DDS Names
            ddslist = ([name.strip() for name in strnames.split(',') if name != ''])

        return ddslist

    def get_BamApiUsername(self):
        apiusername = self.searchMatch("username", self.fileinput)

        username = ""

        if apiusername:
            strapiusername = apiusername[0]
            #username = apiuser1
            username = strapiusername[11:]

        return username

    def get_BamApiPassword(self):
        apipassword= self.searchMatch("password", self.fileinput)

        password = ""

        if apipassword:
            strapipassword = apipassword[0]
            #password = d8e8fca
            password = strapipassword[11:]

        return password

    def get_Action(self):
        actionalert = self.searchMatch("actionalert", self.fileinput)
        actionblock = self.searchMatch("actionblock", self.fileinput)

        alert = 0;
        block = 0;
        if actionalert:
            stractionalert = actionalert[0]
            alert = int(stractionalert[14:])

        if actionblock:
            stractionblock = actionblock[0]
            block = int(stractionblock[14:])
        #actionalert = 0
        #actionalert = 1
        #actionblock = 0
        #actionblock = 1

        # Return array [alert, block]
        # [0, 0] = Both disabled
        # [1, 0] = Alert enabled, Block disabled
        # [0, 1] = Alert disabled, Block enabled
        # [1, 1] = Both enabled
        return [alert, block]

    def get_QueryLength(self):
        querylength = self.searchMatch("querylength", self.fileinput)

        # Initialize to minimum value if not set
        length = 35
        if querylength:
            strquerylength = querylength[0]
            #querylength = 70
            length = int(strquerylength[14:])

            if length < 35:
                return 35
            else:
                return length

    def get_QueryRate(self):
        queryrate = self.searchMatch("queryrate", self.fileinput)

        # Initialize to minimum query value if not set
        rate = 8
        if queryrate:
            strqueryrate = queryrate[0]
            #queryrate = 110
            rate = int(strqueryrate[12:])

            if rate < 8:
                return 8
            else:
                return rate

    def searchMatch(self, word, arrString):
        return filter(lambda x: word in x, arrString)
