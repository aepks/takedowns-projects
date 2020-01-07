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
            "1JRcWGXM_KOfFOzNYdNrH71XbymgYNeiWCXHoi-6ST1U")
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
        responses = self.responseSheet.get_all_values()[1:]
        responses.reverse()
        responses_dict = {}
        for response in responses:
            if response[1] not in responses_dict.keys():
                responses_dict[response[1]] = response[1:]
        return list(responses_dict.values())

    def updateTakedownsForm(self, tid, assignments):
        # Input types:
        # tid: Integer
        # assignments: Tuple of form (pname1, pname2, pname3)
        assignment = ", ".join(assignments)
        cell = "C" + str([2, 3, 5, 6, 8, 9, 11, 12, 14, 15][tid])
        self.takedownsSheet.update_acell(cell, assignment)
        return True

    def getPenalties(self):
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

if __name__ == "__main__":
    session = Session()
    print(session.sheet.get_all_values())
