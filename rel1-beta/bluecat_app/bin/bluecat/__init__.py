"""
The BlueCat Python API. This collection of classes provides access to the BlueCat BAM API as well
as other features of BlueCat's products usually only accessible via direct database access, 
ssh and nsupdate.
"""

from api import api
from api_exception import api_exception
from configuration import configuration
from deployment_role import deployment_role
from entity import entity
from host_record import host_record
from ip4_address import ip4_address
from ip4_block import ip4_block
from ip4_network import ip4_network
from ip6_address import ip6_address
from bdds_server import server
from user import user
from view import view
from zone import zone

# added to work with documentation generation
try:
    import wrappers
except ImportError:
    import os
    import sys
    sys.path.insert(0,os.path.abspath('bluecat'))
    print sys.path

"""
The route() function is a replacement for the Flask standard app.route function. Its purpose is to provide
segregation between custom workflows in terms of function namespace and endpoint URL. Using route() allows
workflows to use overlapping function names to serve endpoints. 
    :param app: The Flask application instance.
    :param path: The full path of the endpoint which must always start with /workflowname.
    :param methods: HTTP methods supported by the endpoint.
"""
def route(app, path, methods=['GET']):
    bits = path.split('/')
    if len(bits) < 2:
        raise Exception('path must start with at least /workflowname')
        
    def func_wrapper(func):
        app.add_url_rule(path, bits[1] + func.__name__, func, methods=methods)
    return func_wrapper
