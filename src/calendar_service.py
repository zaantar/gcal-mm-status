from __future__ import print_function
import datetime
import pickle
import os.path
# noinspection PyPackageRequirements
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
# noinspection PyPackageRequirements
from google.auth.transport.requests import Request

import models.user_settings
import settings
from models.event import Event

# If modifying these scopes, delete the token.pickle.* files.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
TOKEN_FILE_ROOT = '../credentials/'
CREDENTIALS_FILE = '../credentials/google.json'


def get_token_file(user: models.user_settings.UserSettings):
    return TOKEN_FILE_ROOT + user.gcal_token_file


def get_service(user: models.user_settings.UserSettings):
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


def get_upcoming_events(user: models.user_settings.UserSettings):
    service = get_service(user)
    if service is None:
        return []

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    formatted_events = []
    if not events:
        return []
    for event in events:
        formatted_events.append(
            Event(event['id'], event['start'], event['end'], event['summary'], user)
        )

    return formatted_events
