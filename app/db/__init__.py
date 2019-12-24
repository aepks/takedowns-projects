import sqlite3
import datetime

class Session:
    def createCursor(self):
        self.conn = sqlite3.connect("./db/takedowns.db")
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def readAvailability(self, data):  # Takes a list as an arg.
        email = data[0]
        pname = data[1]
        availibility = data[2]

        c = self.createCursor()
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        uid = None
        for row in c:
            uid = row[0]
        if uid:
            self.updateName(uid, pname)
            self.addAvailibility(uid, availibility)
        else:
            uid = self.addUser(email, pname)
            self.addAvailibility(uid, availibility)
        c.close()

    def addUser(self, email, pname):
        c = self.createCursor()
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (None, pname, email))
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
        return tdScore - penaltyScore

    def getDates(self, startDate, endDate):  # Working
        c = self.createCursor()
        return [x for x in c.execute("SELECT dateId, tid FROM schedule WHERE date BETWEEN ? AND ?", (startDate, endDate))]

    def clearDate(self, dateId):
        c = self.createCursor()
        c.execute("DELETE FROM assignments WHERE dateId = ?", (dateId,))
        self.commit()
        c.close()
        return True

    def getAssignments(self, dateId):
        c = self.createCursor()
        try:
            ret = c.execute("SELECT uid FROM assignments WHERE dateId = ?",(dateId,))
            ret = bool(ret.fetchone())
            # print(ret)
            c.close()
            return ret
        except Exception: # If there's no rows returned
            c.close()
            return None

    def assignUser(self, dateId, uid):
        c = self.createCursor()
        c.execute("INSERT INTO assignments VALUES (?, ?)", (dateId, uid))
        c.close()
        self.commit()
        return True


# if __name__ == "__main__":
#     conn = sqlite3.connect("takedowns.db")
#     c = conn.cursor()
#     # vals = [x for x in c.execute("SELECT dateId, tid FROM schedule WHERE date <= ?", ("2020-04-28T00:00:00",)).fetchall()]
#     # print(vals)
#     #
#     # conn = sqlite3.connect("takedowns.db")
#     # c = conn.cursor()
#     nonDays = [
#         (20, 1, 2020),
#         (16, 3, 2020),
#         (17, 3, 2020),
#         (18, 3, 2020),
#         (19, 3, 2020),
#         (20, 3, 2020)
#     ]
#     forbiddenDays = []
#     for day in nonDays:
#         forbiddenDays.append(datetime.datetime(day=day[0], month=day[1], year=day[2]))
#
#     start = datetime.datetime(day=13, month=1, year=2020)
#     date = start
#     end = datetime.datetime(day=9, month=5, year=2020)
#
#     days = [0, 2, 4, 6, 8]
#
#     while (end-start) >= (date-start):
#         if date.weekday() < 5:
#             if date not in forbiddenDays:
#                 base_tid = days[date.weekday()]
#                 c.execute("INSERT INTO schedule VALUES (?, ?, ?)", (None, date.isoformat(), base_tid))
#                 c.execute("INSERT INTO schedule VALUES (?, ?, ?)", (None, date.isoformat(), base_tid + 1))
#         date = date + datetime.timedelta(days=1)
#     #
#     c.close()
#     conn.commit()

    # ddl = (
    #     """
    #     CREATE TABLE IF NOT EXISTS takedowns (
    #         tid INTEGER PRIMARY KEY AUTOINCREMENT,
    #         day TEXT,
    #         meal TEXT
    #     )
    #     """,
    #     """
        # CREATE TABLE IF NOT EXISTS schedule (
        #     dateId INTEGER PRIMARY KEY AUTOINCREMENT,
        #     date TIMESTAMP,
        #     tid INTEGER,
        #     FOREIGN KEY (tid) REFERENCES takedowns
		# )

    #     )
    #     """,
    #     """
    #     CREATE TABLE IF NOT EXISTS users (
    #         uid INTEGER PRIMARY KEY AUTOINCREMENT,
    #         pname TEXT,
    #         email TEXT UNIQUE
    #     )
    #     """,
    #     """
    #     CREATE TABLE IF NOT EXISTS avalibility (
    #         uid INT,
    #         tid INT,
    #         PRIMARY KEY (uid, tid),
    #         FOREIGN KEY (uid) REFERENCES users,
    #         FOREIGN KEY (tid) REFERENCES takedowns
    #     )
    #     """,
    #     """
        # CREATE TABLE IF NOT EXISTS assignments (
        #     dateId INT,
        #     uid INT,
        #     PRIMARY KEY (dateId, uid),
        #     FOREIGN KEY (uid) REFERENCES users,
        #     FOREIGN KEY (dateId) REFERENCES schedule
        # )
    #     """,
    #     """
    #     CREATE TABLE IF NOT EXISTS penalties (
    #         timestamp TEXT,
    #         uid INT,
    #         penalty NUMERIC,
    #         FOREIGN KEY (uid) REFERENCES users,
    #         PRIMARY KEY (timestamp, uid)
    #     )
    #     """,
    # """
    # CREATE VIEW tdScores AS
    # SELECT uid, count(uid) AS tdScore
    # FROM assignments
    # GROUP BY uid;
    # """,
    # """
    # CREATE VIEW penaltyScores AS
    # SELECT uid, sum(penalty) AS penaltyScore
    # FROM penalties
    # GROUP BY uid;
    # """
    # )
    #
    # [c.execute(table) for table in ddl]
    # conn.commit()
    #
    # meals = ("Lunch", "Dinner")
    # days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")
    #
    # i = 0
    # for day in days:
    #     for meal in meals:
    #         c.execute("INSERT INTO takedowns VALUES (?, ?, ?)", (i, day, meal))
    #         i += 1
    # conn.commit()
