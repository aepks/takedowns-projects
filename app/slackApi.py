import requests


# Documentation: https://api.slack.com/messaging/sending

class Session:
    def __init__(self):
        self.api_url = "https://hooks.slack.com/services/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"

    def postTakedowns(self, day, users):
        message = "Takedowns for {day}:"
