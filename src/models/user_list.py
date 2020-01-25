from models.user_settings import UserSettings


class UserList:
    _users: [UserSettings] = []

    def __init__(self, users: [UserSettings]):
        self._users = users

    def get_users(self) -> [UserSettings]:
        return self._users
