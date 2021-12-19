import logging
import os
import json
from keycloak import KeycloakOpenID
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError
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

    def refresh_token_(self, refresh_token):
        try:
            _refreshed_token = self.refresh_token(refresh_token=refresh_token)
            logger.debug('_refreshed_token: {}'.format(_refreshed_token))
            return _refreshed_token
        except Exception as err:
            logger.error('refresh_token() failed! err: {}'.format(err))
            return False

    def introspect_access_token(self, access_token):
        try:
            token_info = self.introspect(access_token)
            logger.debug('token_info: {}'.format(token_info))
            if self.introspect(access_token)['active']:
                return True
            else:
                return False
        except Exception as err:
            logger.error('introspect_token() failed! err: {}'.format(err))
            return False

    def get_user_info(self, access_token):
        try:
            user_info = self.userinfo(token=access_token)
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

    def logout(self, refresh_token):
        self.logout(refresh_token=refresh_token)


class KeycloakAdminHandler(KeycloakAdmin):
    def __init__(self, server_url, realm_name, password):
        super().__init__(server_url=server_url,
                         client_id='admin-cli',
                         realm_name=realm_name,
                         username='realm_admin_user',
                         password=password,
                         auto_refresh_token=["get", "put", "post", "delete"])

    @staticmethod
    def __decode_error_message(error_object: KeycloakError) -> tuple:
        """
        this method will cast the KeycloakError object value to a string
        Args:
            error_object:

        Returns:

        """
        try:
            if isinstance(error_object, KeycloakError):
                error_response_code = error_object.response_code
                error_message = json.loads(error_object.error_message.decode("utf-8"))
                # todo: this can be stupid, maybe there are more interesting information,
                #  not just the 1st element, need to be tested
                message = list(error_message.values())[0]
                return error_response_code, message
            else:
                logger.error("no class of KeycloakError")
                raise Exception("no class of KeycloakError")
        except Exception as err:
            logger.error(err)

    def create_user_(self, payload, exist_ok=False):
        try:
            return self.create_user(payload=payload, exist_ok=exist_ok)
        except KeycloakError as err:
            return self.__decode_error_message(error_object=err)

    def delete_user_(self, user_id):
        try:
            return self.delete_user(user_id=user_id)
        except KeycloakError as err:
            return self.__decode_error_message(error_object=err)

    def delete_client_role_(self, client_role_id, role_name):
        try:
            return self.delete_client_role(client_role_id=client_role_id, role_name=role_name)
        except KeycloakError as err:
            return self.__decode_error_message(error_object=err)

    def create_client_role_(self, client_role_id, payload, skip_exists=False):
        try:
            return self.create_client_role(client_role_id=client_role_id, payload=payload, skip_exists=skip_exists)
        except KeycloakError as err:
            return self.__decode_error_message(error_object=err)

    def get_client_role_(self, client_id, role_name):
        try:
            return self.get_client_role(client_id=client_id, role_name=role_name)
        except KeycloakError as err:
            return self.__decode_error_message(error_object=err)

    def get_user_id_(self, username):
        try:
            return self.get_user_id(username=username)
        except KeycloakError as err:
            return self.__decode_error_message(error_object=err)

    def get_user_(self, user_id):
        try:
            return self.get_user(user_id=user_id)
        except KeycloakError as err:
            return self.__decode_error_message(error_object=err)

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

    def get_users_(self, query):
        query["limit"] = 10
        # see https://erogol.com/timeout-function-takes-long-finish-python/
        if isinstance(query, dict):
            try:
                return self.get_users(query=query)
            except KeycloakError as err:
                return self.__decode_error_message(error_object=err)
        else:
            return 400, "bad request"

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

    def create_realm_role_(self, payload, skip_exists=False):
        result = self.create_realm_role(payload=payload, skip_exists=skip_exists)
        return result





