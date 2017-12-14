from suds import WebFault
from suds.client import Client
from bluecat.api_exception import api_exception

def add_entity(soap_client, parent, entity_object, version='8.1.0'):
    """
    A generic method for adding configurations, DNS zones, and DNS resource records.
    When using addEntity() to add a zone, you must specify a single zone name without any . (dot)
    characters.

    :param self:
    :param parent:
    :param entity_object:
    :return:    the object ID for the new configuration
    """
    try:
        return soap_client.service.addEntity(parent, entity_object)
    except WebFault as e:
        raise api_exception(e.message)

def delete_entity(soap_client, id, version='8.1.0'):
    """
    Deletes an object using the generic delete() method

    :param soap_client:
    :param id:
    :return:
    """
    try:
        return soap_client.service.delete(id)
    except WebFault as e:
        raise api_exception(e.message)

def update_entity(soap_client, api_entity, version='8.1.0'):
    """
    Generic method for updating an object

    :param soap_client:
    :param api_entity:  The actual API entity passed as an entire object that has its mutable
                        values updated
    :return:
    """
    try:
        return soap_client.service.update(api_entity)
    except WebFault as e:
        raise api_exception(e.message)

def link_entities(soap_client, id_one=0, id_two=0, properties=[], version='8.1.0'):
    try:
        return soap_client.service.linkEntities(id_one, id_two, '')
    except WebFault as e:
        raise api_exception(e.message)

def unlink_entities(soap_client, id_one=0, id_two=0, properties=[], version='8.1.0'):
    try:
        return soap_client.service.unlinkEntities(id_one, id_two, properties)
    except WebFault as e:
        raise api_exception(e.message)
