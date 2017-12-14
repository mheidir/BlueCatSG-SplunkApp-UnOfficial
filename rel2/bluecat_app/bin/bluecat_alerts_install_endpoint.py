import splunk.admin as admin
import splunk.entity as en
# import your required python modules


class ConfigApp(admin.MConfigHandler):
  def setup(self):
    if self.requestedAction == admin.ACTION_EDIT:
      for arg in ['bamip', 'username', 'password', 'configuration', 'responsepolicy', 'ddsnames', 'querylength', 'queryrate', 'actionalert', 'actionblock']:
        self.supportedArgs.addOptArg(arg)

  def handleList(self, confInfo):
    confDict = self.readConf("bluecat")
    if None != confDict:
      for stanza, settings in confDict.items():
        for key, val in settings.items():
          if key in ['bamip'] and val in [None, '']:
            val = ''
          confInfo[stanza].append(key, val)

          if key in ['username'] and val in [None, '']:
            val = '127.0.0.1'
          confInfo[stanza].append(key, val)

          if key in ['password'] and val in [None, '']:
            val = ''
          confInfo[stanza].append(key, val)

          if key in ['configuration'] and val in [None, '']:
            val = ''
          confInfo[stanza].append(key, val)

          if key in ['responsepolicy'] and val in [None, '']:
            val = ''
          confInfo[stanza].append(key, val)

          if key in ['ddsnames'] and val in [None, '']:
            val = ''
          confInfo[stanza].append(key, val)

          if key in ['querylength'] and val in [None, '']:
            val = '35'
          confInfo[stanza].append(key, val)

          if key in ['queryrate'] and val in [None, '']:
            val = '8'
          confInfo[stanza].append(key, val)

          if key in ['actionalert'] and val in [None, '']:
            val = '0'
          confInfo[stanza].append(key, val)

          if key in ['actionblock'] and val in [None, '']:
            val = '0'
          confInfo[stanza].append(key, val)

  def handleEdit(self, confInfo):
    name = self.callerArgs.id
    args = self.callerArgs

    self.writeConf('bluecat', 'bamidentity', self.callerArgs.data)

# initialize the handler
admin.init(ConfigApp, admin.CONTEXT_NONE)
