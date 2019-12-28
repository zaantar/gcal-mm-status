import mattermostdriver
import json
import requests
import enum
import log

log.set_log_level(log.Level.DEBUG)


class Status(enum.Enum):
    ONLINE = 'online'
    AWAY = 'away'
    DND = 'dnd'
    OFFLINE = 'offline'


with open('../credentials/mattermost.json') as jsonFile:
    credentials = json.load(jsonFile)

server_url = credentials['server']
token = credentials['token']

log.l('Interacting with a Mattermost server at %s...' % server_url, log.Level.INFO)


class TokenAuth(requests.auth.AuthBase):
    def __call__(self, r):
        # Implement my authentication
        r.headers['Authorization'] = "Bearer %s" % token
        return r


driver = mattermostdriver.Driver({
    'url': server_url,
    'scheme': 'https',
    'port': 443,
    'auth': TokenAuth,
})

user_cache = {}


def get_user(user_login):
    if user_login in user_cache:
        return user_cache[user_login]
    log.l('Retrieving user information for %s...' % user_login, log.Level.INFO)
    user = driver.users.get_user_by_username(user_login)
    user_cache[user_login] = user
    log.l('User id of "%s" is "%s".' % (user_login, user['id']), log.Level.DEBUG)
    return user


def parse_response(response):
    is_ok = response.ok;
    if not is_ok:
        log.l("Response not OK: %d %s" % (response.status_code, response.reason), log.Level.INFO)
    return is_ok


def get_user_id(user_login):
    user = get_user(user_login)
    if user is None:
        return None
    user_id = user['id']
    return user_id


def set_user_status(user_login, status):
    log.l('Setting status of user "%s" to "%s"...' % (user_login, status.value), log.Level.INFO)
    user_id = get_user_id(user_login)
    data = {
        'status': status.value,
        'user_id': user_id
    }
    log.l('Making the request...', log.Level.DEBUG)
    response = driver.client.make_request('put', '/users/%s/status' % user_id, data=json.dumps(data))
    return parse_response(response)


def set_user_suffix(user_login, suffix):
    log.l('Setting the nickname suffix of user "%s" to "%s"...' % (user_login, suffix), log.Level.INFO)
    user = get_user(user_login)
    if user is None:
        return False
    prev_nickname = user['nickname']
    nickname_base = prev_nickname.split('|')[0]
    new_nickname = nickname_base + '|' + suffix
    log.l('Making the request...', log.Level.DEBUG)
    response = driver.client.make_request(
        'put',
        '/users/%s/patch' % get_user_id(user_login),
        data=json.dumps({'nickname': new_nickname})
    )
    return parse_response(response)


set_user_status('jan', Status.DND)
set_user_suffix('jan', 'test2')
