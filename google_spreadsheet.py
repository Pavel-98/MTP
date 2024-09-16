from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_cred(TOKEN_PATH=None):
    global creds
    try:
        token = os.environ['GOOGLE_SHEETS_TOKEN']
        refresh_token = os.environ['GOOGLE_REFRESH_TOKEN']
        token_uri = os.environ['GOOGLE_TOKEN_URI']
        client_id = os.environ['GOOGLE_CLIENT_ID']
        client_secret = os.environ['GOOGLE_CLIENT_SECRET']
        creds = Credentials(token=token, refresh_token=refresh_token, token_uri=token_uri, client_id=client_id, client_secret=client_secret, scopes=SCOPES)
    except Exception as e:
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    return creds

class GoogleSpreadsheetsService:

    def __init__(self, TOKEN_PATH=None):
        self.creds = get_cred(TOKEN_PATH)
        self.service = build('sheets', 'v4', credentials=creds)
        self.spreadsheets = self.service.spreadsheets()

    def get_values_of_sheet(self, spreadsheet_id, sheet_title):
        return self.spreadsheets.values().get(spreadsheetId=spreadsheet_id, range=sheet_title).execute()['values']

    def append_values(self, spreadsheet_id, sheet_title, values):
        body = {'values': values}
        self.spreadsheets.values().append(spreadsheetId=spreadsheet_id, range=sheet_title, valueInputOption="USER_ENTERED", body=body).execute()

    def create_sheet(self, spreadsheet_id, sheet_title):
        data = {'requests': [
            {
                'addSheet': {
                    'properties': {'title': sheet_title}
                }
            }

        ]}
        id = self.spreadsheets.batchUpdate(spreadsheetId=spreadsheet_id, body=data).execute()['replies'][0]['addSheet']['properties']['sheetId']
        return id

    def clear_sheet(self, spreadsheet_id, sheet_title):
        self.spreadsheets.values().clear(spreadsheetId=spreadsheet_id, range=sheet_title).execute()

    def update_value(self, spreadsheet_id, sheet_title, row, column, value):
        body = {'values': [[value]]}
        range = f"{sheet_title}!R{row}C{column}:R{row}C{column}"
        self.spreadsheets.values().update(spreadsheetId=spreadsheet_id, range=range, body=body, valueInputOption="USER_ENTERED").execute()