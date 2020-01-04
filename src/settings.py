import json
from typing import List, Any

import log
import re

with open('../settings.json') as jsonFile:
    rawSettings = json.load(jsonFile)

log.l('settings:' + json.dumps(rawSettings), log.Level.DEBUG)


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


class EventPattern:
    pattern = ''
    flags = []
    suffix = ''
    status = ''

    def __init__(self, pattern_settings):
        self.pattern = pattern_settings['pattern']
        self.flags = pattern_settings['flags']
        self.suffix = pattern_settings['suffix']
        self.status = pattern_settings['status']

    def get_re_flags(self):
        flag_values = [eval('re.%s' % flag_name) for flag_name in self.flags]
        result = 0
        for flag_value in flag_values:
            result |= flag_value
        return result

    def is_match(self, event_summary):
        regex_pattern = re.compile(self.pattern, self.get_re_flags())
        match = re.search(regex_pattern, event_summary)
        return match is not None


class UserSettings:
    mattermost_login = ''
    gcal_token_file = ''
    patterns: List[EventPattern] = []

    def __init__(self, user_settings):
        self.mattermost_login = user_settings['mattermost_login']
        self.gcal_token_file = user_settings['gcal_token_file']
        for pattern_settings in user_settings['patterns']:
            self.patterns.append(EventPattern(pattern_settings))
