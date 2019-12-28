import mattermostdriver
import json
import requests
import enum


class Status(enum.Enum):
    ONLINE = 'online'
    AWAY = 'away'
    DND = 'dnd'
    OFFLINE = 'offline'


with open('../credentials/mattermost.json') as jsonFile:
    credentials = json.load(jsonFile)

server_url = credentials['server']
token = credentials['token']
username = 'jan'

print(server_url)
print(token)


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

user = driver.users.get_user_by_username(username)
user_id = user['id']
user_sub_url = '/users/' + user_id


def set_user_status(status):
    data = {
        'status': status,
        'user_id': user_id
    }
    return driver.client.make_request('put', user_sub_url + '/status', data=json.dumps(data))


print(set_user_status('away'))
