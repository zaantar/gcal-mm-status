from models.user_settings import UserSettings


class UserList:
    users: [UserSettings] = []

    def __init__(self, users: [UserSettings]):
        self.users = users
