from suds import WebFault
from suds.client import Client
from bluecat.api_exception import api_exception

def get_entity_by_name(soap_client, parent_id, name, type, version='8.1.0'):
    """
    Returns objects from the database referenced by their name field

    :param soap_client:
    :param parent_id:
    :param name:
    :param type:
    :return:
    """
    try:
        return soap_client.service.getEntityByName(parent_id, name, type)
    except WebFault as e:
        raise api_exception(e.message)

def get_entity_by_id(soap_client, id):
    """
    Returns objects from the database referenced by their database ID and with its properties fields populated

    :param soap_client:
    :param id:
    :return:
    """
    try:
        return soap_client.service.getEntityById(id)
    except WebFault as e:
        raise api_exception(e.message)

def get_entities(soap_client, parent_id, type, start, count, version='8.1.0'):
    """
    Returns an array of requested child objects for a given parent_id value

    :param soap_client:
    :param parent_id:
    :param type:
    :param start:
    :param count:
    :return:
    """
    try:
        return soap_client.service.getEntities(parent_id, type, start, count)
    except WebFault as e:
        raise api_exception(e.message)

def get_parent(soap_client, id, version='8.1.0'):
    """
    Returns the APIEntity for the parent entity with its properties fields populated

    :param soap_client:
    :param id:  The id of the entity whose parent you want to retrieve
    :return:
    """
    try:
        return soap_client.service.getParent(id)
    except WebFault as e:
        raise api_exception(e.message)

def get_linked_entities(soap_client, entity_id, type, start=0, count=100, version='8.1.0'):
    try:
        return soap_client.service.getLinkedEntities(entity_id, type, start, count)
    except WebFault as e:
        raise api_exception(e.message)
