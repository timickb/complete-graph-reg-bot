import httplib2
import apiclient.discovery
import logging
import settings

from pprint import pprint
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
    
    def _get_insert_visit_request(self, visitor : Visitor,):
        """ Возвращает тело запроса для добавления посетителя в таблицу """
        return {
            "majorDimension": "ROWS",
            "values": [visitor.get_sheet_row()]
        }

    def _get_formula_expansion_request(self, last_row_index : int):
        """ Возвращает тело запроса для копирования формулы рассчета
        времени и чека в строку с индексом last_row_index + 1 """
        return {
            'requests': [
                {
                    'copyPaste': {
                        "source": {
                            'sheetId': self.sheet_id,
                            'startRowIndex': 1,
                            'startColumnIndex': settings.TIME_FORMULA_COLUMN_ID,
                            'endRowIndex': 2,
                            'endColumnIndex': settings.RECEIPT_FORMULA_COLUMN_ID + 1
                        },
                        "destination": {
                            'sheetId': self.sheet_id,
                            'startRowIndex': last_row_index - 1,
                            'startColumnIndex': settings.TIME_FORMULA_COLUMN_ID,
                            'endRowIndex': last_row_index,
                            'endColumnIndex': settings.RECEIPT_FORMULA_COLUMN_ID + 1
                        },
                        "pasteType": "PASTE_FORMULA"
                    }
                }
            ]
        }
    
    def register_visitor(self, name, surname, tariff):
        """ Записывает в таблицу посетителя с именем name (+ surname) и тарифом tariff """

        # Корректность значения tariff гарантируется.
        visitor = Visitor(name, surname, float(tariff))

        insert_visit_response = self.service.spreadsheets().values().append(
            spreadsheetId = self.spreadsheet_id,
            range = "A1:E1",
            valueInputOption = "USER_ENTERED",
            body = self._get_insert_visit_request(visitor)).execute()
        
        # Получение номера последней строки.
        last_row_index = int(insert_visit_response['updates']['updatedRange'].split(':')[-1][1:])

        # Запрос на копирование формул.
        self.service.spreadsheets().batchUpdate(
            spreadsheetId = self.spreadsheet_id,
            body = self._get_formula_expansion_request(last_row_index)).execute()
        
        