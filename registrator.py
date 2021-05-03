import httplib2
import googleapiclient.discovery
import logging
import settings

from pprint import pprint
from oauth2client.service_account import ServiceAccountCredentials
from visitor import Visitor
from datetime import datetime

class Registrator:

    def __init__(self, credentials_file, spreadsheet_id, sheet_id):
        self.credentials_file = credentials_file
        self.spreadsheet_id = spreadsheet_id
        self.sheet_id = sheet_id
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.credentials_file, 
            ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
        self.httpAuth = self.credentials.authorize(httplib2.Http())
        self.service = googleapiclient.discovery.build('sheets', 'v4', http = self.httpAuth)
    
    def __get_insert_visit_request(self, visitor : Visitor,):
        """ Возвращает тело запроса для добавления посетителя в таблицу """
        return {
            "majorDimension": "ROWS",
            "values": [visitor.get_sheet_row()]
        }

    def __get_formula_expansion_request(self, last_row_index : int) -> dict:
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
    
    def register_visitor(self, name, surname, tariff, comment) -> int:
        """ Записывает в таблицу посетителя с именем name, фамилией surname, тарифом tariff 
        и опционально с комментарием, возвращает идентификатор нового посетителя"""

        # Корректность значения tariff гарантируется.
        visitor = Visitor(name, surname, float(tariff), comment)

        insert_visit_response = self.service.spreadsheets().values().append(
            spreadsheetId = self.spreadsheet_id,
            range = "A1:H1",
            valueInputOption = "USER_ENTERED",
            body = self.__get_insert_visit_request(visitor)).execute()
        
        # Получение номера последней строки.
        last_row_index = int(insert_visit_response['updates']['updatedRange'].split(':')[-1][1:])

        # Запрос на копирование формул.
        self.service.spreadsheets().batchUpdate(
            spreadsheetId = self.spreadsheet_id,
            body = self.__get_formula_expansion_request(last_row_index)).execute()
        
        # Возвращаем номер последней строки в качестве идентификатора посетителя.
        return last_row_index
    
    def get_visitor_receipt(self, visitor_id : int) -> str:
        """ Возвращает ответное сообщение на команду выставления счета посетителю """

        try:
            # Проверим посетителя на существование. Для этого ячейка с его именем должна быть непустой.
            check_existing_response = self.service.spreadsheets().values().get(
                spreadsheetId = self.spreadsheet_id,
                range = f'A{visitor_id}:B{visitor_id}',
                majorDimension = 'ROWS'
            ).execute()
        except googleapiclient.errors.HttpError:
            return settings.UNKNOWN_VISIT_ID_MESSAGE

        try:
            visit_date = check_existing_response['values'][0][0]
            visitor_name = check_existing_response['values'][0][1]
        except KeyError:
            return settings.UNKNOWN_VISIT_ID_MESSAGE

        # Еще важно, чтобы дата посещения совпадала с текущей датой.
        if datetime.now().strftime("%d.%m") != visit_date:
            return settings.INVALID_VISIT_DATE_MESSAGE

        if len(visitor_name) == 0:
            return settings.UNKNOWN_VISIT_ID_MESSAGE
        
        # Присвоим его ячейке "Убытие" текущее время.
        set_time_response = self.service.spreadsheets().values().batchUpdate(
            spreadsheetId = self.spreadsheet_id,
            body = {
            "valueInputOption": "USER_ENTERED",
            "data": [
                {
                    "range": f'E{visitor_id}:E{visitor_id}',
                    "majorDimension": "ROWS",
                    "values": [[datetime.now().strftime("%H:%M")]]
                }
            ]
        }
        ).execute()

        # Вытаскиваем сумму, которую должен заплатить посетитель.
        receipt_response = self.service.spreadsheets().values().get(
            spreadsheetId = self.spreadsheet_id,
            range = f'F{visitor_id}:G{visitor_id}',
            majorDimension = 'ROWS'
        ).execute()

        spent_time = receipt_response['values'][0][0]
        receipt = receipt_response['values'][0][1]

        return settings.RECEIPT_MESSAGE % (visitor_name, spent_time, receipt)
        
        
