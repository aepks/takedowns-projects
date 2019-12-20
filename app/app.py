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
cur_datetime = datetime.datetime(day=1, month=2, year=200) # Debug. :)
endDate = datetime.datetime(day=5, month=7, year=2020)

# endDate = cur_datetime + datetime.timedelta(days=14)

print(cur_datetime.isoformat(), endDate.isoformat())
# [3] Get dates to solve for:

dates = dbSession.getDates(cur_datetime.isoformat(), endDate.isoformat())

# [4] Reduce dates to remove already solved dates.
for date in dates:
    if dbSession.getAssignments(date[0]):
        continue

    # [5] Solve each of the remaining dates:
    availUsers = dbSession.getAvailibility(date[1])
    chosenUsers = []
    while len(chosenUsers) < 3:
        if len(availUsers) == 0:
            print("Ran out of people! maybe ask Slack?")
            break
        minUser = availUsers[0]
        minUserScore = dbSession.getScore(minUser)
        for user in availUsers:
            if dbSession.getScore(user) < minUserScore:
                minUser = user
        chosenUsers.append(minUser)
        availUsers.remove(minUser)
    for user in chosenUsers:
        dbSession.assignUser(date[0], user)

# [6] Complete?
