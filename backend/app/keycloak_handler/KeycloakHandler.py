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

    def get_client_role_members_(self, client_id, role_name, **query):
        try:
            return self.get_client_role_members(client_id=client_id, role_name=role_name, **query)
        except KeycloakError as err:
            return self.__decode_error_message(error_object=err)

    def assign_client_role_(self, user_id, client_id, roles):
        try:
            return self.assign_client_role(user_id=user_id, client_id=client_id, roles=roles)
        except KeycloakError as err:
            return self.__decode_error_message(error_object=err)

    def create_group_(self, payload, parent=None, skip_exists=False):
        try:
            return self.create_group(payload=payload, parent=parent, skip_exists=skip_exists)
        except KeycloakError as err:
            return self.__decode_error_message(error_object=err)

    def get_groups_(self):
        try:
            return self.get_groups()
        except KeycloakError as err:
            return self.__decode_error_message(error_object=err)

    def get_group_(self, group_id):
        try:
            return self.get_group(group_id=group_id)
        except KeycloakError as err:
            logger.debug(1)
            return self.__decode_error_message(error_object=err)

    def get_group_by_path_(self, path, search_in_subgroups=False):
        try:
            return self.get_group_by_path(path=path, search_in_subgroups=search_in_subgroups)
        except KeycloakError as err:
            return self.__decode_error_message(error_object=err)

    def delete_group_(self, group_id):
        try:
            return self.delete_group(group_id=group_id)
        except KeycloakError as err:
            logger.debug(1)
            return self.__decode_error_message(error_object=err)

    def get_group_members_(self, group_id, **query):
        try:
            return self.get_group_members(group_id=group_id, **query)
        except KeycloakError as err:
            logger.debug(1)
            return self.__decode_error_message(error_object=err)

    def group_user_add_(self, user_id, group_id):
        try:
            return self.group_user_add(user_id=user_id, group_id=group_id)
        except KeycloakError as err:
            return self.__decode_error_message(error_object=err)

    def group_user_remove_(self, user_id, group_id):
        try:
            return self.group_user_remove(user_id=user_id, group_id=group_id)
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
