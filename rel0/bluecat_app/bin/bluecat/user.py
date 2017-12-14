from suds import WebFault

from api_exception import api_exception
from entity import entity
from util import *
from wrappers import user_api
from wrappers import generic_setters as generic_setter
from wrappers import generic_getters as generic_getter

""" BAM user entities.
"""


class user(entity):
    def __init__(self, api, soap_entity, soap_client):
        super(user, self).__init__(api, soap_entity, soap_client)

    def add_to_group(self, group_id, properties=''):
        """
        Link the user to the user group, adding the user to the group

        :param group_id:
        :param properties:
        :return:
        """
        try:
            properties = parse_properties(properties)
            generic_setter.link_entities(self._soap_client, self.get_id(), group_id, properties)
        except WebFault as e:
            raise api_exception(e.message)

    def remove_from_group(self, group_id, properties=''):
        try:
            generic_setter.unlink_entities(self._soap_client, self.get_id(), group_id, properties)
        except WebFault as e:
            raise api_exception(e.message)

    def get_user_groups(self):
        """
        Get any user groups this user belongs to
        :return:
        """
        res = []
        try:
            soap_entities = generic_getter.get_linked_entities(self._soap_client, self.get_id(), 'UserGroup')
        except api_exception as e:
            raise e
        if hasattr(soap_entities, 'item') and len(soap_entities) > 0:
            res += [self._api.instantiate_entity(e, self._soap_client) for e in soap_entities.item]
        return res
