from __future__ import annotations
import enum


class MattermostStatus(enum.Enum):
    ONLINE = 'online'
    AWAY = 'away'
    DND = 'dnd'
    OFFLINE = 'offline'

    @staticmethod
    def from_string(value: str) -> MattermostStatus:
        try:
            return MattermostStatus(value)
        except ValueError:
            return MattermostStatus.ONLINE
