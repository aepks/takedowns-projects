import authenticate


class Session:
    def __init__(self):
        self.service = authenticate.calendar_auth()
        # Do Things
