"""
Shared constants used throughout the application.
"""

"""Number of seconds in a minute"""
MINUTE: int = 60

"""How often to check the calendar for new events."""
CALENDAR_CHECK_POLLING_INTERVAL = MINUTE * 10

"""How often to check the queue for actionable tasks."""
TASK_QUEUE_CHECK_INTERVAL = MINUTE * 0.5


"""
Permission scope for the Google API.

Note: If modifying these scopes, delete the token.pickle.* files.
"""
GOOGLE_API_SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

"""Where are the token files for the Google API located, relative to source root."""
GOOGLE_TOKEN_FILE_ROOT = '../credentials/'

"""Google API credentials (for the app as such)"""
GOOGLE_CREDENTIALS_FILE = '../credentials/google.json'
