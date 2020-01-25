from typing import List

from models.event_pattern import EventPattern


class UserSettings:
    mattermost_login = ''
    gcal_token_file = ''
    patterns: List[EventPattern] = []
    _id: str

    def __init__(self, user_settings):
        self.mattermost_login = user_settings['mattermost_login']
        self.gcal_token_file = user_settings['gcal_token_file']
        for pattern_settings in user_settings['patterns']:
            self.patterns.append(EventPattern(pattern_settings))
        self._id = self.mattermost_login

    def get_id(self):
        return self._id
