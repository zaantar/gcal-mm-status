from __future__ import print_function
import datetime
import pickle
import os.path
# noinspection PyPackageRequirements
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
# noinspection PyPackageRequirements
from google.auth.transport.requests import Request
# noinspection PyPackageRequirements
import google.auth.exceptions
from models.user import User
from models.event import Event
from controllers.logger import Logger
import http.client
import socket
from constants import constants


class CalendarService:
    """
    Handles all communication with the Google Calendar API.
    """
    _services = {}
    _logger: Logger

    def __init__(self, logger: Logger):
        self._logger = logger

    def _get_service(self, user: User):
        user_id = user.get_id()
        if user_id not in self._services:
            self._logger.log('Building calendar service object for user %s...' % user_id)
            self._services[user_id] = CalendarService._build_service(user)
        return self._services[user_id]

    def get_upcoming_events(self, user: User) -> [Event]:
        """Retrieve 10 upcoming events for the given user, including declined and cancelled ones."""
        service = self._get_service(user)
        if service is None:
            return []

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        self._logger.info('Getting the upcoming 10 events', 1)
        try:
            events_result = service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy='startTime',
                showDeleted=True
            ).execute()
            events = events_result.get('items', [])
        except (
                ConnectionResetError, ConnectionAbortedError, google.auth.exceptions.TransportError,
                ConnectionError, ConnectionRefusedError, http.client.RemoteDisconnected, socket.gaierror
        ) as exc:
            self._logger.error('A network-related error occurred while fetching upcoming events: %s' % repr(exc), -1)
            return []
        self._logger.untab()

        formatted_events = []
        if not events:
            return []
        for event in events:
            is_declined = False
            if 'attendees' in event:
                # Eventually, this should be moved to Event itself and taken into account when handling
                # updated events (changed time or acceptance status).
                self_attendees = list(
                    filter(lambda attendee: 'self' in attendee and attendee['self'], event['attendees']))
                declined_self_attendees = list(filter(
                    lambda attendee: 'responseStatus' in attendee and 'declined' == attendee['responseStatus'],
                    self_attendees
                ))
                if len(declined_self_attendees) > 0 and len(declined_self_attendees) == len(self_attendees):
                    is_declined = True

            is_cancelled = ('status' in event and 'cancelled' == event['status'])

            formatted_events.append(
                Event(event['id'], event['start'], event['end'], event['summary'], user, is_cancelled, is_declined)
            )

        return formatted_events

    @staticmethod
    def _build_service(user: User):
        token_file = CalendarService._get_token_file(user)
        creds = None
        # The file token.pickle.* stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(constants.GOOGLE_CREDENTIALS_FILE,
                                                                 constants.GOOGLE_API_SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)
        return service

    @staticmethod
    def _get_token_file(user: User):
        return constants.GOOGLE_TOKEN_FILE_ROOT + user.get_gcal_token_file_name()
