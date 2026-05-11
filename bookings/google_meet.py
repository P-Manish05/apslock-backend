import os
import pickle
from datetime import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_google_service():
    creds = None
    token_path = 'google_token.json'
    credentials_path = 'google_credentials.json'

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)


def create_google_meet(booking_date, start_time, end_time,
                        attendee_name, attendee_email):
    try:
        service = get_google_service()

        start_datetime = datetime.combine(booking_date, start_time)
        end_datetime = datetime.combine(booking_date, end_time)

        start_str = start_datetime.strftime('%Y-%m-%dT%H:%M:%S')
        end_str = end_datetime.strftime('%Y-%m-%dT%H:%M:%S')

        event = {
            'summary': f'APSLOCK Consultation - {attendee_name}',
            'description': f'Free consultation call with APSLOCK team.\nClient: {attendee_name}\nEmail: {attendee_email}',
            'start': {
                'dateTime': start_str,
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_str,
                'timeZone': 'Asia/Kolkata',
            },
            'attendees': [
                {'email': attendee_email},
                {'email': os.getenv('NOTIFY_EMAIL')},
            ],
            'conferenceData': {
                'createRequest': {
                    'requestId': f'apslock-{attendee_email}-{start_str}',
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    }
                }
            },
        }

        event = service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1,
            sendUpdates='all'
        ).execute()

        meet_link = event.get('hangoutLink', '')
        event_id = event.get('id', '')

        print(f"Google Meet created: {meet_link}")
        return meet_link, event_id

    except Exception as e:
        print(f"Google Meet error: {e}")
        return None, None