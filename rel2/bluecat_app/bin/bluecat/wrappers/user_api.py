from suds import WebFault
from bluecat.api_exception import api_exception

def add_user_group(soap_client, name, properties='', version='8.1.0'):
    try:
        return soap_client.service.addUserGroup(name, properties)
    except WebFault as e:
        raise api_exception(e.message)

def add_user(soap_client, username, password, properties='', version='8.1.0'):
    try:
        return soap_client.service.addUser(username, password, properties)
    except WebFault as e:
        raise api_exception(e.message)


