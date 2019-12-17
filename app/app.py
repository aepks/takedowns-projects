import db
import responseForms
import datetime

dbSession = db.Session()
responseForms = responseForms.Session()

# [1] - Reimport Response Data
responses = responseForms.getResponses()
for response in responseForms.getResponses():
    dbSession.readAvailability(response)

# [2] Calculate date to get values to.
# The remainder of the current week, if necessary, plus the following week.

cur_datetime = datetime.datetime.now()
cur_datetime = datetime.datetime(day=13, month=1, year=2020) # Debug. :)

if cur_datetime.weekday() < 5:  # If it's M-F of the current week:
    endDate = cur_datetime + datetime.timedelta(days=(7 + 5 - cur_datetime.weekday()))

# [3] Get dates to solve for:

dates = dbSession.getDates(cur_datetime.isoformat(), endDate.isoformat())

# [4] Reduce dates to remove already solved dates.

for date in dates:
    if dbSession.getAssignments(date[0]):
        dates.remove(date)

# [5] Solve each of the remaining dates:
