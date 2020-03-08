import mattermostdriver
import json
from requests import auth
import sys
from constants.log_level import LogLevel
from controllers.logger import Logger


def parse_nickname_parts(nickname):
    nickname_parts = nickname.split('|')
    if len(nickname_parts) == 0:
        return ''
    if len(nickname_parts) < 2:
        return {'base': nickname_parts[0], 'suffix': ''}
    return {'base': nickname_parts[0], 'suffix': nickname_parts[1]}


class MattermostService:
    """
    Service that fully encapsulates the interaction with Mattermost.
    """
    _logger: Logger
    _driver: mattermostdriver.Driver
    _user_cache = {}

    def __init__(self, logger: Logger):
        self._logger = logger
        with open('../credentials/mattermost.json') as jsonFile:
            credentials = json.load(jsonFile)

        server_url = credentials['server']
        token = credentials['token']

        self._logger.log('Interacting with a Mattermost server at %s...' % server_url, LogLevel.INFO)

        class TokenAuth(auth.AuthBase):
            def __call__(self, r):
                # Implement my authentication
                r.headers['Authorization'] = "Bearer %s" % token
                return r

        self._driver = mattermostdriver.Driver({
            'url': server_url,
            'scheme': 'https',
            'port': 443,
            'auth': TokenAuth,
        })

    def _get_user(self, user_login):
        if user_login in self._user_cache:
            return self._user_cache[user_login]
        self._logger.log('Retrieving user information for %s...' % user_login, LogLevel.INFO)
        user = self._driver.users.get_user_by_username(user_login)
        self._user_cache[user_login] = user
        self._logger.log('User id of "%s" is "%s".' % (user_login, user['id']), LogLevel.DEBUG)
        return user

    def _parse_response(self, response):
        is_ok = response.ok
        if not is_ok:
            self._logger.log("Response not OK: %d %s" % (response.status_code, response.reason), LogLevel.INFO)
        return is_ok

    def _get_user_mattermost_id(self, user_login):
        user = self._get_user(user_login)
        if user is None:
            return None
        user_id = user['id']
        return user_id

    def set_user_status(self, user_login, status) -> bool:
        self._logger.log('Setting status of user "%s" to "%s"...' % (user_login, status.value), LogLevel.INFO)
        # noinspection PyBroadException
        try:
            user_id = self._get_user_mattermost_id(user_login)
            data = {
                'status': status.value,
                'user_id': user_id
            }
            self._logger.log('Making the request...', LogLevel.DEBUG)
            response = self._driver.client.make_request('put', '/users/%s/status' % user_id, data=json.dumps(data))
            return self._parse_response(response)
        except:
            self._logger.error(
                'A network-related error occurred while setting user stats: %s'
                % str(sys.exc_info()[0]), -1
            )
            return False

    def set_user_suffix(self, user_login, suffix) -> bool:
        self._logger.log(
            'Setting the nickname suffix of user "%s" to "%s"...' % (user_login, suffix),
            LogLevel.INFO
        )
        # noinspection PyBroadException
        try:
            user = self._get_user(user_login)
            if user is None:
                return False
            prev_nickname = user['nickname']
            nickname_parts = parse_nickname_parts(prev_nickname)
            new_nickname = nickname_parts['base'] + '|' + suffix
            self._logger.log('Making the request...', LogLevel.DEBUG)
            response = self._driver.client.make_request(
                'put',
                '/users/%s/patch' % self._get_user_mattermost_id(user_login),
                data=json.dumps({'nickname': new_nickname})
            )
            user['nickname'] = new_nickname
            return self._parse_response(response)
        except:
            self._logger.error(
                'A network-related error occurred while setting user nickname: %s'
                % str(sys.exc_info()[0]), -1
            )
            return False

    def get_user_suffix(self, user_login) -> str:
        user = self._get_user(user_login)
        if user is None:
            return ''
        return parse_nickname_parts(user['nickname'])['suffix']
