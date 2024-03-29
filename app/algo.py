import app.db as db
import app.mail as mail
import app.responseForms as responseForms
import datetime
import math
from dateutil.parser import parse


class Session:
    def __init__(self):
        self.dbSession = db.Session()
        self.responseForms = responseForms.Session()
        self.penalties = {
            "Food Not Put Away": .5,  # 1/2
            "Intense Dirty Dishes": .35,  # 1/3
            "Mild Dirty Dishes": .20,  # 1/5
            "Intense Dirty Food Warmers": .25,  # 1/2
            "Mild Dirty Food Warmers": .17,  # 1/6
            "Intense Serving Table Not Wiped": .25,  # 1/4
            "Mild Serving Table Not Wiped": .20,  # 1/5
            "Utensils Not Ran": 0.20,  # 1/5
            "Cutting Boards Not Cleaned": 0.10  # 1/10
        }

    def readResponseForms(self):
        for response in self.responseForms.getResponses():
            self.dbSession.readAvailability(response)

    def readPenalties(self):
        penalties = self.responseForms.getPenalties()
        # print(penalties)
        for penalty in penalties:
            date = penalty[0]
            meal = penalty[3]
            penaltiesApplied = penalty[2]
            if date:
                penaltyDateTime = parse(date)
            simplePenaltyDateTime = datetime.datetime(
                day=penaltyDateTime.day, month=penaltyDateTime.month, year=penaltyDateTime.year)
            spdtif = simplePenaltyDateTime.isoformat()
            date = self.dbSession.getDate(spdtif)

            if not date:
                # print(date)
                # print("Fuckaroo, bud")
                # print(spdtif)
                return False

            if meal == "Lunch":
                penaltyMeal = date
            else:
                penaltyMeal = date + 1

            penaltyScore = 0
            for penalty in penaltiesApplied.split(", "):
                penaltyScore += self.penalties[penalty]

            penaltyScore = round(penaltyScore, 2)
            assignedUsers = self.dbSession.getAssignments(penaltyMeal)

            for user in assignedUsers:
                self.dbSession.applyPenalty(
                    date, user, penaltyScore, penaltiesApplied)
                # Sending penalty email. This will probably get ugly.
                to = self.dbSession.getEmail(user)
                subject = f"Penalty of {penaltyScore} applied to your takedown."
                message = f"""
                <h2>{self.dbSession.getPname(user)},</h2>
                <h3>Penalty Info:</h3>
                <ul>
                <li><strong>Penalty Size: </strong>{penaltyScore}</li>
                <li><strong>Penalties applied: </strong> {penaltiesApplied}</li>
                <li><strong>Current Penalty Balance: </strong>{round(self.dbSession.getPenaltyBalance(user), 2)}</li>
                <li><strong>Meal: </strong>{meal}</li>
                <li><strong>Date: </strong>{spdtif}</li>
                </ul>
                <br>
                <p>If you'd like to appeal this penalty, please reply to this email.</p>
                <br>
                <p><i>This message was automatically generated by the Takedowns Automation Project.</i><p>
                """
                mail.SendMessage(to, subject, message, message)

    def updateTakedowns(self):
        curDate = datetime.datetime.now()
        if curDate.weekday() < 5:
            weekStart = curDate - datetime.timedelta(days=curDate.weekday())
        else:
            weekStart = curDate + \
                datetime.timedelta(days=(7 - curDate.weekday()))
        dates = self.dbSession.getDates(
            weekStart, weekStart + datetime.timedelta(days=5))

        assignmentList = []
        for date in dates:
            dateId, tid = date
            assignmentUids = self.dbSession.getAssignments(dateId)
            assignments = [self.dbSession.getPname(
                uid).strip() for uid in assignmentUids]
            assignmentList.append((tid, assignments))

        self.responseForms.updateTakedownsForm(assignmentList)

    def solveDates(self, startDate=None, endDate=None):
        if not startDate or not endDate:
            startDate = datetime.datetime(day=1, month=2, year=200)  # DEBUG
            endDate = datetime.datetime(day=5, month=7, year=20200)
        dates = self.dbSession.getDates(
            startDate.isoformat(), endDate.isoformat()) # list of (dateId, tid)
        for date in dates:
            if self.dbSession.getAssignments(date[0]):
                continue
            availUsers = self.dbSession.getAvailibility(date[1]) # list of UIDs
            chosenUsers = []
            newMemberChosen = False
            while availUsers and len(chosenUsers) < 2:
                tdScoreUsers = []
                # print(availUsers)
                userScores = [(uid, self.dbSession.getScore(uid)) for uid in availUsers]
                userScores = sorted(userScores, key=lambda x: x[1])
                minScore = userScores[0][1]
                # getScore returns TDScore - penaltyScore. 
                # format: [(uid, score)]

                for user in userScores:
                    if user[1] == minScore:
                        tdScoreUsers.append(user)
                        # print("User ", user[0], " not added.")

                # Now, tdScoreUsers contains a list of all users with lowest score.
                availUserTDDate = filter(lambda x: x != None, ((user[0], 
                    self.dbSession.getMostRecentTakedown(user[0], date[0]), 
                    self.dbSession.getTid(self.dbSession.getMostRecentTakedown(user[0], date[0])))
                for user in tdScoreUsers))

                sortedUserTDDates = sorted(
                    availUserTDDate, key = lambda x: x[1]) # I think this was responsible for the bug. 

                # print(sortedUserTDDates)

                for user in sortedUserTDDates:
                    delta = date[0] - user[1]
                    # if(date[0] - user[1] == date[1] - user[2]):
                    #     delta += 100 # highly disincentivize two takedowns a week
                    if len(chosenUsers) == 2:
                        break
                    if delta < 7:
                        availUsers.remove(user[0])
                        continue
                    if self.dbSession.isNewMember(user[0]) and newMemberChosen:
                        availUsers.remove(user[0])
                        continue
                    elif self.dbSession.isNewMember(user[0]) and not newMemberChosen:
                        newMemberChosen = True
                        chosenUsers.append(user[0])
                        availUsers.remove(user[0])
                    elif not self.dbSession.isNewMember(user[0]):
                        chosenUsers.append(user[0])
                        availUsers.remove(user[0])

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
            dates=self.dbSession.getDates(
                startDate.isoformat(), endDate.isoformat())
        else:  # Only endDate specified
            return False
        for date in dates:
            self.dbSession.clearDate(date[0])
        return True

    def getAssignments(self, startDate = None, endDate = None):
        dates=self.dbSession.getDates(startDate, endDate)
        assignments=[[] for x in range(math.ceil(len(dates) / 5) + 1)]
        currentIndex=0
        for date in dates:
            if len(assignments[currentIndex]) == 5:
                currentIndex += 1
            assigned=self.dbSession.getAssignments(date[0])
            data=[None, []]
            for uid in assigned:
                data[1].append(self.dbSession.getPname(uid))
            dateValString=self.dbSession.getIsoDate(date[0])
            d=datetime.datetime.strptime(dateValString, "%Y-%m-%dT%H:%M:%S")
            dateString=["Monday", "Tuesday", "Wednesday",
                          "Thursday", "Friday"][d.weekday()]
            if date[1] % 2 == 0:
                dateString += " Lunch"
            else:
                dateString += " Dinner"
            dateString += f" {d.month}/{d.day}"
            data[0] = dateString
            assignments[currentIndex].append(data)
        return assignments

    def awardGoodBoyPoint(self, email, points, description):
        dt = datetime.datetime.now().isoformat()
        uid = self.dbSession.getUid(email)
        points = float(points * -1)
        self.dbSession.applyPenalty(dt, uid, points, description)

    def close(self):
        self.dbSession.close()

if __name__ == "__main__":
    s = Session()
    # s.readResponseForms()
    s.clearDates(datetime.datetime(day=1, month=2, year=2021))
    s.solveDates()
    s.updateTakedowns()
