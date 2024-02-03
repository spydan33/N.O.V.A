from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


import traceback
import os
import base64
from bs4 import BeautifulSoup
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/calendar.readonly']

class email_handler:
    class std_email:
        def __init__(self):
            self.id = ''
            self.snippet = ''
            self.body = ''
            self.subject = ''
            self.unread = False

        def dump(self):
            return {
                'id': self.id,
                'snippet': self.snippet,
                'body': self.body,
                'subject': self.subject,
                'unread': self.unread
            }

    def __init__(self):
        self.creds = None

    """ def get_creds_backup_old(self):
        print("hit")
        try:
            if self.creds and (not self.creds.valid and self.creds != False):
                print("1")
                if self.creds.expired and self.creds.refresh_token:
                    print("refresh")
                    self.creds.refresh(Request())
                else:
                    print("3")
            else:
                print("2")
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', 
                    ['https://www.googleapis.com/auth/gmail.readonly']
                )
                self.creds = flow.run_local_server(port=0)
            
            return self.creds
        except HttpError as error:
            print(f'An error occurred: {error}')
            traceback.print_exc()
        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc() """
    
    def get_creds(self):
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
        self.creds = creds
        return creds

    def last(self):
        try:
            creds = self.get_creds()
            service = build('gmail', 'v1', credentials=creds)
            results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=1).execute()
            messages = results.get('messages', [])

            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                if(msg is None or len(msg) < 1):
                    continue
                email_object = self.__format_object(msg)
                break
            if(email_object is None):
                email_object = False
            return email_object
        
        except HttpError as error:
            print('An error occurred: %s' % error)
            
            traceback.print_exc()
        except Exception as e:
            # Handle other exceptions
            print(f"An error occurred: {e}")
            traceback.print_exc()

    def get(self,n_emails):
        try:
            creds = self.get_creds()
            service = build('gmail', 'v1', credentials=creds)
            results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=n_emails).execute()
            messages = results.get('messages', [])

            email_list = []
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                if(msg is None or len(msg) < 1):
                    continue
                email_object = self.__format_object(msg)
                if(email_object is None):
                    continue
                email_list.append(email_object)
            return email_list
        
        except HttpError as error:
            print('An error occurred: %s' % error)
            traceback.print_exc()
            return []
        except Exception as e:
            # Handle other exceptions
            print(f"An error occurred: {e}")
            traceback.print_exc()
            return []


    def __format_object(self,msg):
        obj = self.std_email()
        obj.id = msg['id']
        obj.snippet = msg['snippet']
        payload = msg["payload"]
        headers = payload['headers']
        #body_temp = base64.b64decode(msg["payload"]['body']['data']).decode('utf-8')
        if 'parts' in payload:  # Multipart email
            data = ''
            for part in payload['parts']:
                if('body' in part and 'data' in part['body']):
                    data += part['body']['data']
                else:
                    continue
        else:  # Single part email
            data = payload['body']['data']
        body_temp = base64.urlsafe_b64decode(data).decode('UTF-8')
        soup = BeautifulSoup(body_temp, 'html.parser')
        body = soup.get_text()
        obj.body = body
        for header in msg["payload"]['headers']:
            if(header['name'] == 'Subject'):
                obj.subject = header['value']
                break
        return obj