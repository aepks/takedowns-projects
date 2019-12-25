import gspread
from oauth2client.service_account import ServiceAccountCredentials


class Session:
    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            './responseForms/credentials.json', scope
        )

        self.gc = gspread.authorize(credentials)
        self.responseWks = self.gc.open_by_key(
            "1JRcWGXM_KOfFOzNYdNrH71XbymgYNeiWCXHoi-6ST1U")
        self.responseSheet = self.responseWks.worksheet(
            "Form Responses 1")

        self.takedownsWks = self.gc.open_by_key(
            "1imtbQeB367RogqzJ5hnPXW8U8BzTkMUOL4-fmqBm2Rw"
        )
        self.takedownsSheet = self.takedownsWks.worksheet(
            "Takedowns"
        )

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

        # Use datetime.weekday() and tid to get day, lunch/dinner
        # Then concatenate all three pnames to a string, and update it.

        assignment = ", ".join(assignments)
        cell = "C" + str([2, 3, 5, 6, 8, 9, 11, 12, 14, 15][tid])
        self.takedownsSheet.update_acell(cell, assignment)
        return True

    def getPenalties(self):
        pass


if __name__ == "__main__":
    session = Session()
    print(session.sheet.get_all_values())
