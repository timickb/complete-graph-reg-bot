from datetime import datetime


class Visitor:
    def __init__(self, name, surname, tariff):
        self.tariff = str(tariff).replace(".", ",")
        self.name = name
        self.surname = surname
        self.visitMonthDay = datetime.now().strftime("%d.%m")
        self.visitTime = datetime.now().strftime("%H:%M")
    
    def get_sheet_row(self):
        return [str(self.visitMonthDay), 
                str(self.name) + ' ' + str(self.surname),
                str(self.visitTime),
                str(self.tariff), "-"]