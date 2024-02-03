from __future__ import print_function
import json
import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import traceback
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/calendar.readonly']

class calendar():
    def __init__(self,nova = False):
        if(nova != False):
            self.upcoming_events = self.upcoming(10)
            counter = 0
            for event in self.upcoming_events:
                with open(f'json_data/fuzzy_data/events/event{counter}.json', 'w') as file:
                    json.dump(event, file)
                counter = counter + 1
        self.nova = nova

        #nova.events.on('face_verified',self.update_nova_on_upcoming)

    def creds():
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds

    def upcoming(self,n_events):
        try:
            creds = calendar.creds()
            service = build('calendar', 'v3', credentials=creds)

            # Call the Calendar API
            now = datetime.datetime.now().isoformat() + 'Z'  # 'Z' indicates UTC time
            # Call the Calendar API to fetch the list of calendars
            calendars_result = service.calendarList().list().execute()

            # Get all calendars
            calendars = calendars_result.get('items', [])

            all_events = []

            # Iterate through each calendar and fetch events
            for calendar_sub in calendars:
                calendar_id = calendar_sub['id']
                if(calendar_sub['summary'] not in ["socraticphantom@gmail.com","daniel@cashet.com"]):
                    continue
                
                #print('Fetching events from calendar: %s' % calendar_sub['summary'])
                # Fetch the next n_events from the current calendar
                events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                                    maxResults=n_events, singleEvents=True,
                                                    orderBy='startTime').execute()
                events = events_result.get('items', [])
                
                # Extend the all_events list with the events from the current calendar
                all_events.extend(events)
            sorted_events = sorted(all_events, key=self.get_event_start)

            """ events_result = service.events().list(calendarId='primary', timeMin=now,
                                                maxResults=n_events, singleEvents=True,
                                                orderBy='startTime').execute()
            events = events_result.get('items', []) """

            if len(sorted_events) == 0:
                print('No upcoming events found.')
                ret = False
            else:
                print("upcoming")
                print(len(sorted_events))
                ret = sorted_events

            # Prints the start and name of the next 10 events
            return ret

        except HttpError as error:
            print('An error occurred: %s' % error)
    
    def get_today(self):
        try:
            creds = calendar.creds()
            service = build('calendar', 'v3', credentials=creds)

            now = datetime.datetime.now().isoformat() + 'Z'  # 'Z' indicates UTC time
            #Get todays date
            today_utc = datetime.datetime.utcnow().date()

            # Create a datetime object for the end of the day in UTC
            end_of_day_utc = datetime.datetime.combine(today_utc, datetime.time(23, 59, 59, 999999))

            # Convert to ISO format and append 'Z' for UTC time
            end_of_day_utc_iso = end_of_day_utc.isoformat() + 'Z'
            print(f"start time {now}")
            print(f"end time {end_of_day_utc_iso}")

            calendars_result = service.calendarList().list().execute()

            # Get all calendars
            calendars = calendars_result.get('items', [])

            all_events = []

            # Iterate through each calendar and fetch events
            for calendar_sub in calendars:
                calendar_id = calendar_sub['id']
                if(calendar_sub['summary'] not in ["socraticphantom@gmail.com","daniel@cashet.com"]):
                    continue
                
                #print('Fetching events from calendar: %s' % calendar_sub['summary'])
                # Fetch the next n_events from the current calendar
                events_result = service.events().list(calendarId=calendar_id, timeMin=now, timeMax = end_of_day_utc_iso,
                                                    maxResults=20, singleEvents=True,
                                                    orderBy='startTime').execute()
                events = events_result.get('items', [])
                
                # Extend the all_events list with the events from the current calendar
                all_events.extend(events)
                #print(all_events)

            sorted_events = sorted(all_events, key=self.get_event_start)
            
            if len(sorted_events) == 0:
                print('No upcoming events found.')
                ret = False
            else:
                print("upcoming")
                print(len(sorted_events))
                ret = sorted_events

            # Prints the start and name of the next 10 events
            return ret

        except HttpError as error:
            print('An error occurred: %s' % error)
            return False

    def update_nova_on_upcoming(self):
        nova_string = "Daniel's calenders events are: "
        today_events = self.get_today()
        if(today_events != False):
            for event in today_events:
                
                if("dateTime" in event["start"]):
                    date_object = datetime.datetime.fromisoformat(event["start"]["dateTime"])
                else:
                    continue
                start_time = date_object.strftime('%H:%M')
                nova_string += f"{event.get('summary', 'Work Meeting')} at {start_time},"
        
        if(self.upcoming_events != False):
            
            count = 0
            for event in self.upcoming_events:
                if(count == 3):
                    break
                if("dateTime" in event["start"]):
                    date_object = datetime.datetime.fromisoformat(event["start"]["dateTime"]).replace(tzinfo=None)
                else:
                    continue
                start_time = date_object.strftime('%H:%M')
                current_date = datetime.datetime.now()
                time_difference = date_object - current_date
                time_difference_days = time_difference.days + 1
                if time_difference_days == 0:
                    continue
                elif time_difference_days == 1:
                    time_away = "tomorrow"
                # Check if the date is the day after tomorrow
                elif time_difference_days == 2:
                    time_away = "the day after tomorrow"
                # Check if the date is x days away (change x to the desired number of days)
                else:
                    time_away = f"{time_difference_days} days away"
                nova_string += f"{event.get('summary', 'Work Meeting')} {time_away} at {start_time},"
                count = count + 1
        nova_string += f" <REMEMBER THESE AS YOU WILL BE ASKED ABOUT THEM>" 
        self.nova.OAI.system_message(nova_string)

    def get_event_start(self,event):
        start = event.get('start', {})
        # Using a far future date as a fallback for sorting
        return start.get('dateTime', start.get('date', '9999-12-31T23:59:59Z'))

