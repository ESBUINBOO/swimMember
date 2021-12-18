import logging
import os
from keycloak import KeycloakOpenID
from keycloak import KeycloakAdmin
import sys

logger = logging.getLogger('KEYCLOAK_LOGGER')
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class KeycloakHandler(KeycloakOpenID):
    def __init__(self, server_url, client_id, realm_name, client_secret_key):
        super().__init__(server_url, client_id, realm_name, client_secret_key)

    @staticmethod
    def __decode_return_message(error_message):
        logger.debug(error_message)
        logger.debug(type(error_message))
        pass

    def create_token(self, user_name, password):
            try:
                token = self.token(username=user_name, password=password,)
                return token
            except Exception as err:
                logger.error('Error in create_token() err: {}'.format(err))

    def refresh_token(self, token):
        try:
            _refreshed_token = self.keycloak_openid.refresh_token(token['refresh_token'])
            logger.debug('_refreshed_token: {}'.format(_refreshed_token))
            return _refreshed_token
        except Exception as err:
            logger.error('refresh_token() failed! err: {}'.format(err))
            return False

    def introspect_access_token(self, access_token):
        try:
            token_info = self.keycloak_openid.introspect(access_token)
            logger.debug('token_info: {}'.format(token_info))
            if self.keycloak_openid.introspect(access_token)['active']:
                return True
            else:
                return False
        except Exception as err:
            logger.error('introspect_token() failed! err: {}'.format(err))
            return False

    def get_user_info(self, access_token):
        try:
            user_info = self.keycloak_openid.userinfo(token=access_token)
            if type(user_info) is dict:
                return user_info
            else:
                return False
        except Exception as err:
            logger.error('get_user_info() failed! err: {}'.format(err))
            return False

    def validate_and_refresh_token(self, token_to_validate):
        _token_is_valid = self.introspect_access_token(access_token=token_to_validate)
        if not _token_is_valid:
            logger.info('Access Token is invalid, trying to refresh')
            new_token = self.refresh_token(token=token_to_validate)
            if type(new_token) is not dict:
                _token_is_valid = False
            else:
                _token_is_valid = self.introspect_access_token(access_token=new_token)
        if _token_is_valid:
            _result = True
            _refreshed_token = token_to_validate
        else:
            _result = False
            _refreshed_token = None
        return _result, _refreshed_token

    def logout(self, token):
        self.keycloak_openid.logout(token['refresh_token'])


class KeycloakAdminHandler(KeycloakAdmin):
    def __init__(self, server_url, realm_name, password):
        super().__init__(server_url=server_url,
                         client_id='admin-cli',
                         realm_name=realm_name,
                         username='realm_admin_user',
                         password=password)

    def get_user_id_(self, user_name):
        try:
            logger.debug('get_user_id() with user_name {}'.format(user_name))
            return self.get_user_id(username=user_name)
        except Exception as err:
            logger.error('get_user_id() failed! err: {}'.format(err))
            return False

    def get_user_(self, user_id):
        try:
            logger.debug('get_user() with user_id {}'.format(user_id))
            return self.get_user(user_id=user_id)
        except Exception as err:
            logger.error('get_user() failed! err: {}'.format(err))
            return False

    def get_user_groups_(self, user_id):
        try:
            logger.debug('get_user_groups() with user_id {}'.format(user_id))
            return self.get_user_groups(user_id=user_id)
        except Exception as err:
            logger.error('get_user_groups() failed! err: {}'.format(err))
            return False

    def get_group_(self, group_id):
        return self.get_group(group_id=group_id)

    def get_group_attributes_(self, user_name):
        attributes = {}
        for group in self.get_user_groups_(user_id=self.get_user_id_(user_name=user_name)):
            for k, v in self.get_group(group_id=group['id'])['attributes'].items():
                if k not in attributes:
                    if 'True' in v:
                        v = True
                    elif 'False' in v:
                        v = False
                    attributes.update({k: v})
        return attributes

    def search_user(self, query):
        """
        wrapper function to search a user in keycloak
        if the query is bad, like 1 char, the search runs pretty long, so we need to time it out!
        :param :query Query as a dictionary
        :return found user list
        :rtype list
        :return False if query is not a dict
        """
        # todo: TimeOut handling! [Dominic, Marcel]
        # see https://erogol.com/timeout-function-takes-long-finish-python/
        if type(query) == dict:
            return self.get_users(query=query)
        else:
            return False

    def get_group_id(self, group_name):
        groups = self.get_groups()
        for group in groups:
            if group['name'] == group_name:
                return group['id']

    def insert_user_to_group(self, user_id, group_id):
        try:
            self.group_user_add(user_id=user_id, group_id=group_id)
            return True
        except Exception as err:
            logger.error('insert_user_to_group() failed! err: {}'.format(err))
            return False

    def delete_user_from_group_(self, user_id, group_id):
        try:
            self.delete_user_from_group(user_id=user_id, group_id=group_id)
            return True
        except Exception as err:
            logger.error('delete_user_from_group failed! err: {}'.format(err))
            return False




