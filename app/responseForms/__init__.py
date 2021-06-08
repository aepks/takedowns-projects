import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

class Session:
    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            './app/responseForms/credentials.json', scope
        )

        self.gc = gspread.authorize(credentials)
        self.responseWks = self.gc.open_by_key(
            "1imtbQeB367RogqzJ5hnPXW8U8BzTkMUOL4-fmqBm2Rw")
        self.responseSheet = self.responseWks.worksheet(
            "Form Responses 1")
        self.takedownsWks = self.gc.open_by_key(
            "1imtbQeB367RogqzJ5hnPXW8U8BzTkMUOL4-fmqBm2Rw")
        self.takedownsSheet = self.takedownsWks.worksheet(
            "Takedowns"
        )
        self.penaltiesWks = self.gc.open_by_key(
            "1VPOrmIxbn3PzY71UJXErlM9YZZM54g9vIylKOIqEKLQ")
        self.penaltiesSheet = self.penaltiesWks.worksheet("Penalties")

    def getResponses(self):
        try:
            responses = self.responseSheet.get_all_values()[1:]
            responses.reverse()
            responses_dict = {}
            for response in responses:
                if len(response[0]) < 5:
                    continue
                if response[1] not in responses_dict.keys():
                    responses_dict[response[1]] = response[1:]
            return list(responses_dict.values())
        except Exception:
            self.__init__()
            return self.getResponses()

    def updateTakedownsForm(self, assignmentList):
        cells = []
        TID_KEY = {
            1: 0,
            2: 1,
            3: 3,
            4: 4,
            5: 6,
            6: 7,
            7: 9,
            8: 10,
            9: 12,
            10: 13
        }
        try:
            cells = self.takedownsSheet.range("C2:C15")
            for (tid, assignments) in assignmentList:
                c = cells[(TID_KEY[tid])]
                c.value = ", ".join(assignments)
            self.takedownsSheet.update_cells(cells)
            return True

        except gspread.exceptions.APIError:
            self.__init__()
            return self.updateTakedownsForm(assignmentList)

    def getPenalties(self):
        try:
            penalties = self.penaltiesSheet.get_all_values()[1:]
            row = 1
            ret = []
            for penalty in penalties:
                row += 1
                if len(penalty[4]) > 2:
                    continue
                else:
                    ret.append(penalty)
                    cell = "E" + str(row)
                    self.penaltiesSheet.update_acell(cell, datetime.datetime.now().isoformat())
            return ret
        except Exception:
            self.__init__()
            return self.getPenalties()
