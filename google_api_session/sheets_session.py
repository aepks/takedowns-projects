import authenticate


class Session:
    def __init__(self):
        self.service = authenticate.sheets_auth()
        # Do Things
