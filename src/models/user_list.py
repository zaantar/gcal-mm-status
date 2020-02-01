from models.user import User


class UserList:
    _users: [User] = []

    def __init__(self, users: [User]):
        self._users = users

    def get_users(self) -> [User]:
        return self._users
