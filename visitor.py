from datetime import datetime


class Visitor:
    def __init__(self, name, surname, tariff, comment):
        self.tariff = str(tariff).replace(".", ",")
        self.name = name
        self.surname = surname
        self.comment = comment
        self.visitMonthDay = datetime.now().strftime("%d.%m")
        self.visitTime = datetime.now().strftime("%H:%M")
    
    def get_sheet_row(self) -> list:
        """ Возвращает список из значений параметров посетителя,
        соответствующий строке в таблице """
        return [str(self.visitMonthDay), 
                str(self.name) + ' ' + str(self.surname),
                str(self.visitTime),
                str(self.tariff), '-', '', '',
                str(self.comment)]