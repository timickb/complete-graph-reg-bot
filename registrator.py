from pprint import pprint
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from visitor import Visitor



class Registrator:

    def __init__(self, credentials_file, spreadsheet_id, sheet_id):
        self.credentials_file = credentials_file
        self.spreadsheet_id = spreadsheet_id
        self.sheet_id = sheet_id
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.credentials_file, 
            ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
        self.httpAuth = self.credentials.authorize(httplib2.Http())
        self.service = apiclient.discovery.build('sheets', 'v4', http = self.httpAuth)
    
    def register_visitor(self, name, surname, tariff):
        try:
            tariff = float(tariff)
        except:
            print('Incorrect tariff value')
            return

        visitor = Visitor(name, surname, tariff)

        insert_visit_request_body = {
            "majorDimension": "ROWS",
            "values": [visitor.get_sheet_row()]
        }
        # закидываем в табличку нового челика
        insert_visit_response = self.service.spreadsheets().values().append(
            spreadsheetId = self.spreadsheet_id,
            range = "A1:E1",
            valueInputOption = "USER_ENTERED",
            body = insert_visit_request_body).execute()
        
        # вычисляем номер последней заполненной строки
        last_row_index = int(insert_visit_response['updates']['updatedRange'].split(':')[-1][1:])

        expand_formula_request_body = {
            'requests': [
                {
                    'copyPaste': {
                        "source": {
                            'sheetId': self.sheet_id,
                            'startRowIndex': 1,
                            'startColumnIndex': 5,
                            'endRowIndex': 2,
                            'endColumnIndex': 7 
                        },
                        "destination": {
                            'sheetId': self.sheet_id,
                            'startRowIndex': last_row_index - 1,
                            'startColumnIndex': 5,
                            'endRowIndex': last_row_index,
                            'endColumnIndex': 7
                        },
                        "pasteType": "PASTE_FORMULA"
                    }
                }
            ]
        }

        expand_formula_response = self.service.spreadsheets().batchUpdate(
            spreadsheetId = self.spreadsheet_id,
            body = expand_formula_request_body).execute()
        
        pprint(expand_formula_response)

