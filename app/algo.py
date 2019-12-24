import db
import responseForms
import datetime


class Session:
    def __init__(self):
        self.dbSession = db.Session()
        self.responseForms = responseForms.Session()

    def readResponseForms(self):
        self.responseForms = responseForms.Session()
        for response in responseForms.getResponses():
            self.dbSession.readAvailability(response)

    def solveDates(self, startDate=None, endDate=None):
        if not startDate or not endDate:
            startDate = datetime.datetime(day=1, month=2, year=200)  # Debug.
            endDate = datetime.datetime(day=5, month=7, year=2020)
        dates = self.dbSession.getDates(
            startDate.isoformat(), endDate.isoformat())
        for date in dates:
            if self.dbSession.getAssignments(date[0]):
                continue
            availUsers = self.dbSession.getAvailibility(date[1]).shuffle()
            chosenUsers = []
            while len(chosenUsers) < 3:
                if len(availUsers) == 0:
                    print("Ran out of people! maybe ask Slack?")
                    break
                minUser = availUsers[0]
                minUserScore = int(self.dbSession.getScore(minUser))
                for user in availUsers:
                    if int(self.dbSession.getScore(user)) < minUserScore:
                        minUser = user
                        minUserScore = int(self.dbSession.getScore(user))
                chosenUsers.append(minUser)
                availUsers.remove(minUser)
            for user in chosenUsers:
                self.dbSession.assignUser(date[0], user)

    def clearDates(self, startDate=None, endDate=None):  # Datetime objects
        if not startDate and not endDate:  # Delete all assignments.
            startDate = datetime.datetime(day=1, month=1, year=200).isoformat()
            endDate = datetime.datetime(day=7, month=7, year=2020).isoformat()
            dates = self.dbSession.getDates(startDate, endDate)
        elif not endDate:
            dates = self.dbSession.getDates(
                startDate.isoformat(), startDate.isoformat())
        elif startDate and endDate:
            dates = self.dbSession.getDates(
                startDate.isoformat(), endDate.isoformat())
        else:  # Only endDate specified
            return False
        for date in dates:
            self.dbSession.clearDate(date[0])
        return True
