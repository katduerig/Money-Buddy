# this file talks to google sheets, collects and adds data to sheets

RANGE_NAME= "Sheet1"

import pathlib

import googleapiclient.discovery
from oauth2client import tools, client
from oauth2client.file import Storage

import config

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']



secrets_dir = pathlib.Path('secrets')
if secrets_dir.exists():
    cached_credentials = secrets_dir.joinpath(f'google_credentials_cached.json')
    store = Storage(cached_credentials)
    credentials = store.get()

    if not credentials or credentials.invalid:
        print(f'Credentials were invalid, need auth!')
        flow = client.flow_from_clientsecrets(config.GOOGLE_SECRET_FILEPATH, SCOPES)
        args_to_pass = tools._CreateArgumentParser().parse_args()
        args_to_pass.noauth_local_webserver = True

        credentials = tools.run_flow(flow, store, flags=args_to_pass)

    service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)

    sheet = service.spreadsheets() # boilerplate above here
else:
    sheet = None

# returns entire google spreadsheet in a python list of lists
def get_all_data(): 
    if sheet == None: # if running without secrets (dummy data)
        return [
            [], 
            ['8/31/84', '228.23', 'laundry', 'i have too many shorts', 'jims house', 'i begged for it'],
            ['8/31/84', '100.23', 'bakery', 'i have too many shorts', 'jims house', 'i begged for it'],
            ['7/31/84', '5.23', 'laundry', 'i have too many shorts', 'jims house', 'i begged for it'],
            ['7/31/84', '2.23', 'bakery', 'i have too many shorts', 'jims house', 'i begged for it'],
            ['7/31/84', '9.23', 'personal', 'i have too many shorts', 'jims house', 'i begged for it'],
        ]
    
    result = (
        sheet.values()
        .get(spreadsheetId=config.SPREADSHEET_ID, range=RANGE_NAME)
        .execute()
    )
    values = result.get("values", [])

    if not values:
        print("No data found.")
        exit()

    return values

# adds a row of information to the google sheet
def insert_one_row(when, amount, category, note, where, method): 
    setNote = {
        "insertDimension": {
            "range": {
                "sheetId": 0,
                "dimension": "ROWS",
                "startIndex": 1,
                "endIndex": 2
            },
            "inheritFromBefore": False
        }
    }

    request = service.spreadsheets().batchUpdate(
            spreadsheetId=config.SPREADSHEET_ID, body={"requests": [setNote]})
    request.execute()

    values = [
        [when, amount, category, note, where, method]
    ]
    
    body = {'values': values}
    sheet.values().append(
            spreadsheetId=config.SPREADSHEET_ID, range=RANGE_NAME+'!A2:A2',
            valueInputOption="RAW", body=body).execute()
    
    # New function for inserting income

def insert_income_row(date, amount, source, description):
    setNote = {
    "insertDimension": {
        "range": {
            "sheetId": 0,
            "dimension": "ROWS",
            "startIndex": 1,
            "endIndex": 2
        },
        "inheritFromBefore": False
    }
}
    request = service.spreadsheets().batchUpdate(
            spreadsheetId=config.INCOME_SPREADSHEET_ID, body={"requests": [setNote]})
    request.execute()

    values = [
        [date, amount, source, description]
    ]
    
    body = {'values': values}
    sheet.values().append(
            spreadsheetId=config.INCOME_SPREADSHEET_ID, range="Income"+'!A2:A2',
            valueInputOption="RAW", body=body).execute()

