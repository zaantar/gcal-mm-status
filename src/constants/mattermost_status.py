import enum


class MattermostStatus(enum.Enum):
    ONLINE = 'online'
    AWAY = 'away'
    DND = 'dnd'
    OFFLINE = 'offline'
