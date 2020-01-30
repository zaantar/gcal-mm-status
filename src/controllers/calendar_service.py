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

from models.user_settings import UserSettings
import settings
from models.event import Event
from controllers.logger import Logger
from constants.log_level import LogLevel

# If modifying these scopes, delete the token.pickle.* files.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
TOKEN_FILE_ROOT = '../credentials/'
CREDENTIALS_FILE = '../credentials/google.json'


def get_token_file(user: UserSettings):
    return TOKEN_FILE_ROOT + user.gcal_token_file


def build_service(user: UserSettings):
    token_file = get_token_file(user)
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
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service


class CalendarService:
    _services = {}
    _logger: Logger

    def __init__(self, logger: Logger):
        self._logger = logger

    def get_service(self, user: UserSettings):
        user_id = user.get_id()
        if user_id not in self._services:
            self._logger.log('Building calendar service object for user %s...' % user_id)
            self._services[user_id] = build_service(user)
        return self._services[user_id]

    def get_upcoming_events(self, user: UserSettings):
        service = self.get_service(user)
        if service is None:
            return []

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        self._logger.log('Getting the upcoming 10 events')
        try:
            events_result = service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
        except google.auth.exceptions.TransportError as exc:
            self._logger.error('A transport error while fetching upcoming events: %s' % repr(exc))
            return []

        formatted_events = []
        if not events:
            return []
        for event in events:
            formatted_events.append(
                Event(event['id'], event['start'], event['end'], event['summary'], user)
            )

        return formatted_events
