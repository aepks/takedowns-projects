import authenticate
from spreadsheet_config import config


class Session:
    def __init__(self):
        self.service = authenticate.sheets_auth()
        self.takedowns_key = config['takedowns_key']

    def read_takedowns_list(self):
        values = self.service.spreadsheets().values().batchGet(
            spreadsheetId=self.takedowns_key,
            range='D2:D15'
        )

        for value in values
            if not value:
                values.remove(value)

        # Values should contain a list of people on takedowns. Untested.
