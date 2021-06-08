import sqlite3
import datetime
from base64 import b64encode
import os
from sqlite3.dbapi2 import OperationalError
from app.db.ddl import ddl

PATH = "./app/db/takedowns.db"
START = datetime.datetime(day=19, month=1, year=2021)
END = datetime.datetime(day=12, month=12, year=2021)

class Session:
    def __init__(self):
        conn = self.connect()
        c = conn.cursor()
        if len(c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()) == 0:
            print("Regenerating database!")
            for x in ddl:
                c.execute(x)

            meals = ("Lunch", "Dinner")
            days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")

            for day in days:
                for meal in meals:
                    c.execute("INSERT INTO takedowns VALUES (NULL, ?, ?)", (day, meal))

            nonDays = [
                (9, 2, 2021),
                (10, 3, 2021),
                (8, 4, 2021),
                (30, 4, 2021),
            ]
            
            forbiddenDays = []
            for day in nonDays:
                forbiddenDays.append(datetime.datetime(day=day[0], month=day[1], year=day[2]))

            date = START

            days = [1, 3, 5, 7, 9]

            while (END-START) >= (date-START):
                if date.weekday() < 5:
                    if date not in forbiddenDays:
                        base_tid = days[date.weekday()]
                        c.execute("INSERT INTO schedule VALUES (?, ?, ?)", (None, date.isoformat(), base_tid))
                        c.execute("INSERT INTO schedule VALUES (?, ?, ?)", (None, date.isoformat(), base_tid + 1))
                date = date + datetime.timedelta(days=1)

        conn.commit()
        c.close()
        conn.close()

    def connect(self):
        return sqlite3.connect(PATH)

    def readAvailability(self, data):  # Takes a list as an arg.
        newMemberResponse = {
            "Yes": 1,
            "No": 0
        }
        email = data[0]
        pname = data[1]
        availibility = data[2]
        newMember = int(newMemberResponse[data[3]])

        if newMember == 1:
            pname = pname + " (NM)"

        conn = self.connect()
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        uid = None
        for row in c:
            uid = row[0]
        if uid:
            self.updateName(uid, pname)
            self.addAvailibility(uid, availibility)
        else:
            uid = self.addUser(email, pname, newMember)
            self.addAvailibility(uid, availibility)
        c.close()
        conn.close()


    def isNewMember(self, uid):
        conn = self.connect()
        c = conn.cursor()
        v = c.execute("SELECT newMember FROM users WHERE uid = ?", (uid,)).fetchone()
        if v == None:
            raise ValueError("UID not found!" + str(uid))
        
        r = bool(v[0])
        c.close()
        conn.close()
        return r

    def addUser(self, email, pname, newMember):
        conn = self.connect()
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (
            None, pname.strip(), email, newMember))
        c.execute("SELECT last_insert_rowid()")
        uid = c.fetchone()[0]
        conn.commit()
        c.close()
        conn.close()
        return uid

    def updateName(self, uid, pname):
        conn = self.connect()
        c = conn.cursor()
        c.execute("UPDATE users SET pname = ? WHERE uid = ?", (pname, uid,))
        c.close()
        conn.commit()
        conn.close()
        return True

    def addAvailibility(self, uid, avalibility):
        conn = self.connect()
        c = conn.cursor()
        c.execute("DELETE FROM avalibility WHERE uid = ?", (uid,))
        if not avalibility:
            c.close()
            conn.commit()
            conn.close
            return True

        if len(avalibility.split(", ")) > 1:
            for date in avalibility.split(", "):
                vals = date.split()
                day = vals[0]
                meal = vals[1]
                c.execute("SELECT tid FROM takedowns WHERE day = ? AND meal = ?", (day, meal))
                tid = "None"
                for row in c:
                    tid = row[0]
                if tid != "None":
                    c.execute("INSERT INTO avalibility VALUES (?, ?)", (uid, tid))
        else:
            vals = avalibility.split()
            day = vals[0]
            meal = vals[1]
            c.execute("SELECT tid FROM takedowns WHERE day = ? AND meal = ?", (day, meal))
            for row in c:
                tid = row[0]
            c.execute("INSERT INTO avalibility VALUES (?, ?)", (uid, tid))

        conn.commit()
        conn.close()
        return True  # Working

    def getAvailibility(self, tid):  # Working
        conn = self.connect()
        c = conn.cursor()
        ret = [x[0] for x in c.execute("SELECT uid FROM avalibility WHERE tid = ?", (tid,)).fetchall()]
        c.close()
        conn.close()
        return ret

    def getUserAvailibility(self, uid):
        conn = self.connect()
        c = conn.cursor()
        ret = [x[0] for x in c.execute("SELECT tid FROM avalibility WHERE uid = ?", (uid,)).fetchall()]
        c.close()
        conn.close()
        return ret

    def getScore(self, uid):
        conn = self.connect()
        c = conn.cursor()
        tdScore, penaltyScore = 0, 0
        testTdScore = c.execute("SELECT tdScore FROM tdScores WHERE uid = ?", (uid,)).fetchone()
        if testTdScore:
            tdScore = testTdScore[0]
        testPenaltyScore = c.execute("SELECT penaltyScore FROM penaltyScores WHERE uid = ?", (uid,)).fetchone()
        if testPenaltyScore:
            penaltyScore = testPenaltyScore[0]
        c.close()
        conn.close()
        return int(tdScore - penaltyScore)

    def getDates(self, startDate, endDate):  # Working
        conn = self.connect()
        c = conn.cursor()
        ret = [x for x in c.execute("SELECT dateId, tid FROM schedule WHERE date BETWEEN ? AND ?", (startDate, endDate))]
        c.close()
        conn.close()
        return ret

    def getPenaltyBalance(self, uid):
        conn = self.connect()
        c = conn.cursor()
        c.execute("SELECT penaltyScore FROM penaltyScores WHERE uid = ?", (uid,))
        ret = c.fetchone()
        c.close()
        conn.close()
        if ret:
            ret = ret[0]
            return ret
        return 0

    def getTakedownScore(self, uid):
        conn = self.connect()
        c = conn.cursor()
        c.execute("SELECT tdScore from tdScores WHERE uid = ?", (uid,))
        ret = c.fetchone()
        c.close()
        conn.close()
        if ret:
            ret = ret[0]
            return ret
        return 0

    def getAverageTdScore(self):
        conn = self.connect()
        c = conn.cursor()
        c.execute("SELECT avg(tdScore) FROM tdScores")
        ret = round(c.fetchone()[0], 2)
        c.close()
        conn.close()
        return ret

    def getAveragePenaltyScore(self):
        conn = self.connect()
        c = conn.cursor()
        try:
            c.execute("SELECT avg(penaltyScore) FROM penaltyScores")
            ret = round(c.fetchone()[0], 2)
            c.close()
            conn.close()
            return ret
        except Exception:
            c.close()
            conn.close()
            return 0

    def getPenalties(self, uid):
        conn = self.connect()
        c = conn.cursor()
        try:
            ret = [list(x) for x in c.execute("SELECT timestamp, penalty, description FROM penalties WHERE uid = ?", (uid,))]
            c.close()
            conn.close()
            return ret
        except Exception:
            c.close()
            conn.close()
            return 0

    def testEmail(self, email):
        conn = self.connect()
        c = conn.cursor()
        if c.execute("SELECT pname FROM users WHERE email = ?", (email,)).fetchone():
            c.close()
            conn.close()
            return True
        c.close()
        conn.close()
        return False

    def getMostRecentTakedown(self, uid, dateId):
        conn = self.connect()
        c = conn.cursor()
        ret = c.execute("SELECT max(dateId) FROM assignments WHERE uid = ? AND dateId < ?", (uid, dateId)).fetchone()
        c.close()
        conn.close()
        if ret[0]:
            ret = ret[0]
            return ret
        return 0

    def getDate(self, date):
        conn = self.connect()
        c = conn.cursor()
        c.execute("SELECT dateId FROM schedule WHERE date = ? ORDER BY dateId ASC LIMIT 1", (date,))
        ret = c.fetchone()
        if ret:
            ret = ret[0]
            c.close()
            conn.close()
            return ret
        else:
            c.close()
            conn.close()
            return False

    def getTid(self, dateId):
        conn = self.connect()
        c = conn.cursor()
        c.execute("SELECT tid FROM schedule WHERE dateId = ?", (dateId,))
        ret = c.fetchone()
        if ret:
            ret = ret[0]
            c.close()
            conn.close()
            return ret
        else:
            c.close()
            conn.close()
            return False

    def getIsoDate(self, dateId):
        conn = self.connect()
        c = conn.cursor()
        c.execute("SELECT date FROM schedule WHERE dateId = ?", (dateId,))
        ret = c.fetchone()[0]
        c.close()
        conn.close()
        return ret

    def getPname(self, uid):
        conn = self.connect()
        c = conn.cursor()
        c.execute("SELECT pname FROM users WHERE uid = ?", (uid,))
        uid = c.fetchone()[0]
        c.close()
        conn.close()
        return uid

    def getEmail(self, uid):
        conn = self.connect()
        c = conn.cursor()
        c.execute("SELECT email FROM users WHERE uid = ?", (uid,))
        ret = c.fetchone()[0]
        c.close()
        conn.close()
        return ret

    def clearDate(self, dateId):
        conn = self.connect()
        c = conn.cursor()
        c.execute("DELETE FROM assignments WHERE dateId = ?", (dateId,))
        c.close()
        conn.close()
        return True

    def swapAssignment(self, uid, tradeUid, dateId):
        conn = self.connect()
        c = conn.cursor()
        c.execute("UPDATE assignments SET uid = ? WHERE dateId = ? AND uid = ?", (tradeUid, dateId, uid))
        c.close()
        conn.close()

    def getSwapKey(self):
        token = b64encode(os.urandom(10)).decode('utf-8')
        conn = self.connect()
        c = conn.cursor()
        c.execute("INSERT INTO swapTokens VALUES (?)", (token,))
        c.close()
        conn.close()
        return token

    def voidSwapKey(self, token):
        conn = self.connect()
        c = conn.cursor()
        c.execute("DELETE FROM swapTokens WHERE token = ?", (token,))
        rowcount = bool(c.rowcount)
        return rowcount

    def getAssignments(self, dateId):
        conn = self.connect()
        c = conn.cursor()
        try:
            ret = c.execute("SELECT uid FROM assignments WHERE dateId = ?",(dateId,))
            users = []
            for user in ret:
                users.append(user[0])
            c.close()
            conn.close()
            if users:
                return users
            else:
                return []

        except Exception:  # If there's no rows returned
            c.close()
            conn.close()
            return None

    def getUserAssignments(self, uid):
        conn = self.connect()
        c = conn.cursor()
        ret = c.execute("SELECT * FROM assignments WHERE uid = ?", (uid,))
        users = []
        for user in ret:
            users.append(user)
        c.close()
        conn.close()
        if users:
            return users
        else:
            return []

    def assignUser(self, dateId, uid):
        conn = self.connect()
        c = conn.cursor()
        c.execute("INSERT INTO assignments VALUES (?, ?)", (dateId, uid))
        c.close()
        conn.commit()
        conn.close()
        return True

    def applyPenalty(self, timestamp, uid, penalty, description):
        conn = self.connect()
        c = conn.cursor()
        c.execute("INSERT INTO penalties VALUES (?, ?, ?, ?)", (timestamp, uid, penalty, description))
        c.close()
        conn.commit()
        conn.close()
        return True

    def getUid(self, email):
        conn = self.connect()
        c = conn.cursor()
        ret = c.execute("SELECT uid FROM users WHERE email = ?", (email,)).fetchone()[0]
        c.close()
        conn.close()
        return ret

    def getUsers(self):
        conn = self.connect()
        c = conn.cursor()
        c.execute("SELECT email, pname FROM users ORDER BY pname ASC")
        ret = [vals for vals in c]
        c.close()
        return ret

    def getCurMealDateId(self):
        conn = self.connect()
        c = conn.cursor()
        now = datetime.datetime.now()
        hours = now.hour
        if hours < 13.5:
            now = now - datetime.timedelta(hours=13.5)
        elif hours < (18.5):
            now = now - datetime.timedelta(hours=18.5)
        c.execute("SELECT MIN(dateId) FROM schedule WHERE date > ?", (now,))
        ret = c.fetchone()
        c.close()
        conn.close()
        if ret:
            return ret[0]
        return 0

    def getTDStats(self):
        conn = self.connect()
        c = conn.cursor()
        c.execute("SELECT pname, tdScore, IFNULL(penaltyScore, 0) FROM users NATURAL JOIN tdScores LEFT JOIN penaltyScores")
        ret = c.fetchall()
        c.close()
        conn.close()
        return ret

    def close(self):
        return 
