import json

import constants.log_level
import log

from models.user_settings import UserSettings

with open('../settings.json') as jsonFile:
    rawSettings = json.load(jsonFile)

log.l('settings:' + json.dumps(rawSettings), constants.log_level.LogLevel.DEBUG)


def get_default_value(setting_name):
    return ''


def get_setting(setting_name):
    if setting_name in rawSettings:
        return rawSettings[setting_name]
    return get_default_value(setting_name)


user_cache = {}


def get_user_settings(user_login):
    if user_login in user_cache:
        return user_cache[user_login]
    if user_login not in rawSettings['user_settings']:
        return None
    user = UserSettings(rawSettings['user_settings'][user_login])
    user_cache[user_login] = user
    return user


def get_users():
    return list(rawSettings['user_settings'].keys())
