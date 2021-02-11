from app import app
from flask import request, render_template, make_response, redirect, url_for
from app.forms import DateInput, UpdateTakedownsSheet, SolveDateForm, GoodBoyPointForm, DefaultInstacartOrderForm, SaveInstacartOrderSheet, UserLoginForm, TakedownTradeForm
import app.algo as algo
import app.db as db
import app.responseForms as responseForms
import app.instacart as instacart
import app.mail as mail
import datetime

from apscheduler.schedulers.background import BackgroundScheduler

algoSesh = algo.Session()
responseFormsSession = responseForms.Session()
# instacartSession = instacart.Session()

# Scheduler job
def auto_run_scheduler():
    autoRunAlgoSesh = algo.Session()
    startDatetime = datetime.datetime.now()
    endDatetime = datetime.datetime(month=12, day=31, year=2021)

    autoRunAlgoSesh.clearDates(startDatetime, endDatetime)
    autoRunAlgoSesh.solveDates(startDatetime, endDatetime)

    autoRunAlgoSesh.updateTakedowns()
    autoRunAlgoSesh.close()

@app.route("/", methods=['POST', 'GET'])
@app.route("/tdconsole", methods=['POST', 'GET'])
def tdconsole():
    dateInput = DateInput()
    solveDates = SolveDateForm()
    gbpf = GoodBoyPointForm()
    utdsf = UpdateTakedownsSheet()
    dio = DefaultInstacartOrderForm()
    ordersheet = SaveInstacartOrderSheet()

    # if ordersheet.password.data and ordersheet.password.data == "hunter2" and ordersheet.cartChoice.data and ordersheet.validate_on_submit():
    #     cart = ordersheet.cartChoice.data
    #     order = ordersheet.orderChoice.data
    #     responseFormsSession.setInstacartOrder(order, instacartSession.getCartContents(cart))
    message = None
    # if dio.password.data and dio.password.data == "hunter2" and dio.validate_on_submit():
    #     order = responseFormsSession.getInstacartOrder(dio.order.data)
    #     print(order)
    #     for row in order:
    #         print("Adding item. ", row[0], " ", row[2])
    #         instacartSession.addItem(row[0], row[1])

    if gbpf.submit.data and gbpf.validate_on_submit():
        email = gbpf.email.data
        points = gbpf.points.data
        description = gbpf.description.data
        algoSesh.awardGoodBoyPoint(email, points, description)
        message = f"Awarded {points} to {email}."
        return redirect(url_for('.tdconsole'))

    if solveDates.submit.data and solveDates.validate_on_submit():
        algoSesh.readResponseForms()
        algoSesh.readPenalties()
        resetDate = solveDates.resetDate.data + "/2021"
        if solveDates.endResetDate.data:
            endResetDate = solveDates.endResetDate.data + "/2021"
            endDatetime = datetime.datetime.strptime(endResetDate, "%m/%d/%Y")
        else:
            endDatetime = None
        startDatetime = datetime.datetime.strptime(resetDate, "%m/%d/%Y")

        if (startDatetime < datetime.datetime.now()):
            print("Error! I'm redirecting you to google becasue that is what it is")
            return redirect("www.google.com")

        algoSesh.clearDates(startDatetime, endDatetime)
        algoSesh.solveDates(startDatetime, endDatetime)
        algoSesh.updateTakedowns()
        return redirect(url_for('.tdconsole'))

    if dateInput.submit.data and dateInput.validate_on_submit():
        startDate = dateInput.startDate.data + "/2021"
        endDate = dateInput.endDate.data + "/2021"
        startDatetime = datetime.datetime.strptime(startDate, "%m/%d/%Y")
        endDatetime = datetime.datetime.strptime(
            endDate, "%m/%d/%Y") + datetime.timedelta(days=1)
        data = algoSesh.getAssignments(startDatetime, endDatetime)
        resp = make_response(render_template(
            "tdconsole.html", utdsf=utdsf, ordersheet=ordersheet, dio=dio, gbpf=gbpf, message=message, dataRows=data, dateInput=dateInput, clearDate=solveDates))
        resp.set_cookie("startDate", startDate)
        resp.set_cookie("endDate", endDate)
        return resp

    if utdsf.submit.data and utdsf.password.data and utdsf.password.data == "hunter2" and utdsf.validate_on_submit():
        algoSesh.updateTakedowns()

    if "startDate" in request.cookies:
        startDate = request.cookies.get("startDate")
        endDate = request.cookies.get("endDate")
        startDatetime = datetime.datetime.strptime(startDate, "%m/%d/%Y")
        endDatetime = datetime.datetime.strptime(
            endDate, "%m/%d/%Y") + datetime.timedelta(days=1)
        data = algoSesh.getAssignments(startDatetime, endDatetime)
        return render_template("tdconsole.html", utdsf=utdsf, ordersheet=ordersheet, dio=dio, gbpf=gbpf, message=message, dataRows=data, dateInput=dateInput, clearDate=solveDates)

    else:
        startDatetime = datetime.datetime.now() - datetime.timedelta(days=(datetime.datetime.now().weekday()))
        endDatetime = startDatetime + datetime.timedelta(days=40)
        data = algoSesh.getAssignments(startDatetime, endDatetime)
        return render_template("tdconsole.html", utdsf=utdsf, ordersheet=ordersheet, dio=dio, gbpf=gbpf, message=message, dataRows=data, dateInput=dateInput, clearDate=solveDates)

@app.route("/tdtrade", methods=['GET'])
def tdtrade():
    dbSession = db.Session()
    mode = request.args.get('mode')
    token = request.args.get('token')
    uid = request.args.get('uid')
    mealDateId = request.args.get('mealDateId')
    tradeUid = request.args.get('tradeUid')
    if dbSession.voidSwapKey(token):
        if mode == "trade":
            tradeDateId = request.args.get('trade')
            dbSession.swapAssignment(uid, tradeUid, mealDateId)
            dbSession.swapAssignment(tradeUid, uid, tradeDateId)
        if mode == "purchase":
            dbSession.swapAssignment(uid, tradeUid, mealDateId)

    dbSession.close()
    return redirect(url_for('.tdinfo'))

@app.route("/tdinfo", methods=['POST', 'GET'])
def tdinfo():
    dbSession = db.Session()
    userLoginForm = UserLoginForm()
    takedownTradeForm = TakedownTradeForm()
    stats = dbSession.getTDStats()
    print(stats)

    def tdPage(userEmail):
        if userEmail is None:
            user = [None]
        else:
            uid = dbSession.getUid(userEmail)
            pname = dbSession.getPname(uid)
            tdScore = dbSession.getTakedownScore(uid)
            penaltyScore = dbSession.getPenaltyBalance(uid)
            userPenalties = dbSession.getPenalties(uid)
            userAssignments = dbSession.getUserAssignments(uid)
            assignments = []
            if userAssignments:
                for dateId in userAssignments:
                    tid = dbSession.getTid(dateId[0])
                    date = dbSession.getIsoDate(dateId[0])
                    meal = ["Lunch", "Dinner"][tid % 2]
                    day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"][int((tid - tid % 2)/2)]
                    assignments.append([day + " " + meal, date, dateId[0]])

            user = [pname, tdScore, penaltyScore, userPenalties, assignments]

        resp = make_response(render_template(
            "tdinfo.html", user=user, userLoginForm=userLoginForm, takedownTradeForm=takedownTradeForm, stats=stats))

        if userEmail:
            resp.set_cookie("userEmail", userEmail)

        dbSession.close()
        return resp

    if userLoginForm.submit.data and userLoginForm.validate_on_submit():
        userEmail = userLoginForm.email.data
        dbSession.close()
        return tdPage(userEmail)

    if takedownTradeForm.submitData.data and takedownTradeForm.validate_on_submit():
        userEmail = takedownTradeForm.email.data
        uid = dbSession.getUid(userEmail)
        dateId = takedownTradeForm.dateId.data
        tid = dbSession.getTid(dateId)
        traders = dbSession.getAvailibility(tid)
        mail.TakedownTradeMessage(uid, dateId, traders)
        dbSession.close()
        return tdPage(userEmail)

    try:
        userEmail = request.cookies.get("userEmail")
        # dbSession.close()
        return tdPage(userEmail)
    except Exception:
        # dbSession.close()
        return tdPage(None)


sched = BackgroundScheduler()
sched.start()
sched.add_job(auto_run_scheduler, trigger="cron", day_of_week='sat-sun', hour='0-18')
