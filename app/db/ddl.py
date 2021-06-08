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
CREATE VIEW IF NOT EXISTS tdScores  AS
    SELECT uid, count(uid) AS tdScore
    FROM assignments
    GROUP BY uid;
""",
"""
CREATE VIEW IF NOT EXISTS penaltyScores  AS
    SELECT uid, sum(penalty) AS penaltyScore
    FROM penalties
    GROUP BY uid;
"""
)