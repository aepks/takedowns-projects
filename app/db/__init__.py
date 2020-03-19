import sqlite3
import datetime
from base64 import b64encode
import os

class Session:
    def createCursor(self):
        self.conn = sqlite3.connect("./app/db/takedowns.db")
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

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

        c = self.createCursor()
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

    def isNewMember(self, uid):
        c = self.createCursor()
        c.execute("SELECT newMember FROM users WHERE uid = ?", (uid,))
        if c.fetchone()[0] == 1:
            c.close()
            return True
        c.close()
        return False

    def addUser(self, email, pname, newMember):
        c = self.createCursor()
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (
            None, pname.strip(), email, newMember))
        c.execute("SELECT last_insert_rowid()")
        uid = c.fetchone()[0]
        c.close()
        self.commit()
        return uid  # Working

    def updateName(self, uid, pname):
        c = self.createCursor()
        c.execute("UPDATE users SET pname = ? WHERE uid = ?", (pname, uid,))
        c.close()
        self.commit()
        return True  # Working

    def addAvailibility(self, uid, avalibility):
        c = self.createCursor()
        c.execute("DELETE FROM avalibility WHERE uid = ?", (uid,))
        if not avalibility:
            c.close()
            self.commit()
            return True

        if len(avalibility.split(", ")) > 1:
            for date in avalibility.split(", "):
                vals = date.split()
                day = vals[0]
                meal = vals[1]
                c.execute("SELECT tid FROM takedowns WHERE day = ? AND meal = ?", (day, meal))
                for row in c:
                    tid = row[0]
                c.execute("INSERT INTO avalibility VALUES (?, ?)", (uid, tid))
        else:
            vals = avalibility.split()
            day = vals[0]
            meal = vals[1]
            c.execute("SELECT tid FROM takedowns WHERE day = ? AND meal = ?", (day, meal))
            for row in c:
                tid = row[0]
            c.execute("INSERT INTO avalibility VALUES (?, ?)", (uid, tid))
        c.close()
        self.commit()
        return True  # Working

    def getAvailibility(self, tid):  # Working
        c = self.createCursor()
        return [x[0] for x in c.execute("SELECT uid FROM avalibility WHERE tid = ?", (tid,)).fetchall()]

    def getUserAvailibility(self, uid):
        c = self.createCursor()
        return [x[0] for x in c.execute("SELECT tid FROM avalibility WHERE uid = ?", (uid,)).fetchall()]

    def getScore(self, uid):
        c = self.createCursor()
        tdScore, penaltyScore = 0, 0
        testTdScore = c.execute("SELECT tdScore FROM tdScores WHERE uid = ?", (uid,)).fetchone()
        if testTdScore:
            tdScore = testTdScore[0]
        testPenaltyScore = c.execute("SELECT penaltyScore FROM penaltyScores WHERE uid = ?", (uid,)).fetchone()
        if testPenaltyScore:
            penaltyScore = testPenaltyScore[0]
        c.close()
        return int(tdScore - penaltyScore)

    def getDates(self, startDate, endDate):  # Working
        c = self.createCursor()
        return [x for x in c.execute("SELECT dateId, tid FROM schedule WHERE date BETWEEN ? AND ?", (startDate, endDate))]

    def getPenaltyBalance(self, uid):
        c = self.createCursor()
        c.execute("SELECT penaltyScore FROM penaltyScores WHERE uid = ?", (uid,))
        ret = c.fetchone()
        if ret:
            ret = ret[0]
            c.close()
            return ret
        return 0

    def getTakedownScore(self, uid):
        c = self.createCursor()
        c.execute("SELECT tdScore from tdScores WHERE uid = ?", (uid,))
        ret = c.fetchone()
        if ret:
            ret = ret[0]
            c.close()
            return ret
        return 0

    def getAverageTdScore(self):
        c = self.createCursor()
        c.execute("SELECT avg(tdScore) FROM tdScores")
        ret = round(c.fetchone()[0], 2)
        c.close()
        return ret

    def getAveragePenaltyScore(self):
        c = self.createCursor()
        try:
            c.execute("SELECT avg(penaltyScore) FROM penaltyScores")
            ret = round(c.fetchone()[0], 2)
            c.close()
            return ret
        except Exception:
            return 0

    def getPenalties(self, uid):
        c = self.createCursor()
        try:
            ret = [list(x) for x in c.execute("SELECT timestamp, penalty, description FROM penalties WHERE uid = ?", (uid,))]
            c.close()
            return ret
        except Exception:
            return 0

    def testEmail(self, email):
        c = self.createCursor()
        if c.execute("SELECT pname FROM users WHERE email = ?", (email,)).fetchone():
            c.close()
            return True
        c.close()
        return False

    def getMostRecentTakedown(self, uid, dateId):
        c = self.createCursor()
        ret = c.execute("SELECT max(dateId) FROM assignments WHERE uid = ? AND dateId < ?", (uid, dateId)).fetchone()
        c.close()
        if ret[0]:
            ret = ret[0]
            return ret
        print("Couldn't find most recent takedown.")
        return 0

    def getDate(self, date):
        c = self.createCursor()
        c.execute("SELECT dateId FROM schedule WHERE date = ? ORDER BY dateId ASC LIMIT 1", (date,))
        ret = c.fetchone()
        if ret:
            ret = ret[0]
            c.close()
            return ret
        else:
            return False

    def getTid(self, dateId):
        c = self.createCursor()
        c.execute("SELECT tid FROM schedule WHERE dateId = ?", (dateId,))
        ret = c.fetchone()
        if ret:
            ret = ret[0]
            c.close()
            return ret
        else:
            c.close()
            return False

    def getIsoDate(self, dateId):
        c = self.createCursor()
        c.execute("SELECT date FROM schedule WHERE dateId = ?", (dateId,))
        ret = c.fetchone()[0]
        c.close()
        return ret

    def getPname(self, uid):
        c = self.createCursor()
        c.execute("SELECT pname FROM users WHERE uid = ?", (uid,))
        uid = c.fetchone()[0]
        c.close()
        return uid

    def getEmail(self, uid):
        c = self.createCursor()
        c.execute("SELECT email FROM users WHERE uid = ?", (uid,))
        ret = c.fetchone()[0]
        c.close()
        return ret

    def clearDate(self, dateId):
        c = self.createCursor()
        c.execute("DELETE FROM assignments WHERE dateId = ?", (dateId,))
        self.commit()
        c.close()
        return True

    def swapAssignment(self, uid, tradeUid, dateId):
        c = self.createCursor()
        c.execute("UPDATE assignments SET uid = ? WHERE dateId = ? AND uid = ?", (tradeUid, dateId, uid))
        self.commit()
        c.close()

    def getSwapKey(self):
        token = b64encode(os.urandom(10)).decode('utf-8')
        c = self.createCursor()
        c.execute("INSERT INTO swapTokens VALUES (?)", (token,))
        self.commit()
        c.close()
        return token

    def voidSwapKey(self, token):
        c = self.createCursor()
        c.execute("DELETE FROM swapTokens WHERE token = ?", (token,))
        rowcount = bool(c.rowcount)
        self.commit()
        return rowcount

    def getAssignments(self, dateId):
        c = self.createCursor()
        try:
            ret = c.execute("SELECT uid FROM assignments WHERE dateId = ?",(dateId,))
            users = []
            for user in ret:
                users.append(user[0])
            c.close()
            if users:
                return users
            else:
                return []

        except Exception:  # If there's no rows returned
            c.close()
            return None

    def getUserAssignments(self, uid):
        c = self.createCursor()
        ret = c.execute("SELECT * FROM assignments WHERE uid = ?", (uid,))
        users = []
        for user in ret:
            users.append(user)
        c.close()
        if users:
            return users
        else:
            return []

    def assignUser(self, dateId, uid):
        c = self.createCursor()
        c.execute("INSERT INTO assignments VALUES (?, ?)", (dateId, uid))
        c.close()
        self.commit()
        return True

    def applyPenalty(self, timestamp, uid, penalty, description):
        c = self.createCursor()
        c.execute("INSERT INTO penalties VALUES (?, ?, ?, ?)", (timestamp, uid, penalty, description))
        c.close()
        self.commit()
        return True

    def getUid(self, email):
        c = self.createCursor()
        ret = c.execute("SELECT uid FROM users WHERE email = ?", (email,)).fetchone()[0]
        c.close()
        return ret

    def getUsers(self):
        c = self.createCursor()
        c.execute("SELECT email, pname FROM users ORDER BY pname ASC")
        ret = [vals for vals in c]
        c.close()
        return ret

    def getCurMealDateId(self):
        c = self.createCursor()
        now = datetime.datetime.now()
        hours = now.hour
        if hours < 13.5:
            now = now - datetime.timedelta(hours=13.5)
        elif hours < (18.5):
            now = now - datetime.timedelta(hours=18.5)
        c.execute("SELECT MIN(dateId) FROM schedule WHERE date > ?", (now,))
        ret = c.fetchone()
        if ret:
            return ret[0]
        return 0

    def close(self):
        conn.commit()
        conn.close()


if __name__ == "__main__":
    conn = sqlite3.connect("takedowns.db")
    c = conn.cursor()
    ddl = (
        """
        CREATE TABLE IF NOT EXISTS takedowns (
            tid INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT,
            meal TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS schedule (
            dateId INTEGER PRIMARY KEY AUTOINCREMENT,
            date TIMESTAMP,
            tid INTEGER,
            FOREIGN KEY (tid) REFERENCES takedowns
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS users (
            uid INTEGER PRIMARY KEY AUTOINCREMENT,
            pname TEXT,
            email TEXT UNIQUE,
            newMember INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS avalibility (
            uid INT,
            tid INT,
            PRIMARY KEY (uid, tid),
            FOREIGN KEY (uid) REFERENCES users,
            FOREIGN KEY (tid) REFERENCES takedowns
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS assignments (
            dateId INT,
            uid INT,
            PRIMARY KEY (dateId, uid),
            FOREIGN KEY (uid) REFERENCES users,
            FOREIGN KEY (dateId) REFERENCES schedule
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS penalties (
            timestamp TEXT,
            uid INT,
            penalty NUMERIC,
            description TEXT,
            FOREIGN KEY (uid) REFERENCES users,
            PRIMARY KEY (timestamp, uid)
        )
        """,
        """
        CREATE VIEW tdScores AS
        SELECT uid, count(uid) AS tdScore
        FROM assignments
        GROUP BY uid;
        """,
        """
        CREATE VIEW penaltyScores AS
        SELECT uid, sum(penalty) AS penaltyScore
        FROM penalties
        GROUP BY uid;
        """
        )

    [c.execute(table) for table in ddl]
    conn.commit()

    meals = ("Lunch", "Dinner")
    days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")

    i = 0
    for day in days:
        for meal in meals:
            c.execute("INSERT INTO takedowns VALUES (?, ?, ?)", (i, day, meal))
            i += 1

    nonDays = [
        (20, 1, 2020),
        (16, 3, 2020),
        (17, 3, 2020),
        (18, 3, 2020),
        (19, 3, 2020),
        (20, 3, 2020)
    ]
    forbiddenDays = []
    for day in nonDays:
        forbiddenDays.append(datetime.datetime(day=day[0], month=day[1], year=day[2]))

    start = datetime.datetime(day=13, month=1, year=2020)
    date = start
    end = datetime.datetime(day=9, month=5, year=2020)

    days = [0, 2, 4, 6, 8]

    while (end-start) >= (date-start):
        if date.weekday() < 5:
            if date not in forbiddenDays:
                base_tid = days[date.weekday()]
                c.execute("INSERT INTO schedule VALUES (?, ?, ?)", (None, date.isoformat(), base_tid))
                c.execute("INSERT INTO schedule VALUES (?, ?, ?)", (None, date.isoformat(), base_tid + 1))
        date = date + datetime.timedelta(days=1)
    #
    c.close()
    conn.commit()
