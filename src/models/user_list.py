import models.user_settings
import settings


class UserList:
    users: [models.user_settings.UserSettings] = []

    def __init__(self, users: [models.user_settings.UserSettings]):
        self.users = users
