from app import app
from flask import request, render_template, make_response, redirect, url_for
from app.forms import DateInput, UpdateTakedownsSheet, ClearDate, GoodBoyPointForm, emailInput, DefaultInstacartOrderForm
import app.algo as algo
import app.db as db
import app.responseForms as responseForms
import app.instacart as instacart
import datetime

algoSesh = algo.Session()
dbSession = db.Session()
responseFormsSession = responseForms.Session()


@app.route("/", methods=['POST', 'GET'])
@app.route("/tdconsole", methods=['POST', 'GET'])
def tdconsole():
    algoSesh.readResponseForms()
    algoSesh.readPenalties()

    dateInput = DateInput()
    clearDate = ClearDate()
    gbpf = GoodBoyPointForm()
    utdsf = UpdateTakedownsSheet()
    dio = DefaultInstacartOrderForm()

    message = None
    if dio.password.data and dio.password.data == "hunter2" and dio.validate_on_submit():
        instacartSession = instacart.Session()
        for row in responseFormsSession.getDefaultInstacartOrder():
            instacartSession.addItem(row[0], row[2])

    if gbpf.submit.data and gbpf.validate_on_submit():
        email = gbpf.email.data
        points = gbpf.points.data
        description = gbpf.description.data
        algoSesh.awardGoodBoyPoint(email, points, description)
        message = f"Awarded {points} to {email}."
        return redirect(url_for('.tdconsole'))

    if clearDate.submit.data and clearDate.validate_on_submit():
        resetDate = clearDate.resetDate.data + "/2020"
        if clearDate.endResetDate.data:
            endResetDate = clearDate.endResetDate.data + "/2020"
            endDatetime = datetime.datetime.strptime(endResetDate, "%m/%d/%Y")
        else:
            endDatetime = None
        startDatetime = datetime.datetime.strptime(resetDate, "%m/%d/%Y")

        algoSesh.clearDates(startDatetime, endDatetime)
        algoSesh.solveDates(startDatetime, endDatetime)
        return redirect(url_for('.tdconsole'))

    if dateInput.submit.data and dateInput.validate_on_submit():
        startDate = dateInput.startDate.data + "/2020"
        endDate = dateInput.endDate.data + "/2020"
        startDatetime = datetime.datetime.strptime(startDate, "%m/%d/%Y")
        endDatetime = datetime.datetime.strptime(
            endDate, "%m/%d/%Y") + datetime.timedelta(days=1)
        data = algoSesh.getAssignments(startDatetime, endDatetime)
        resp = make_response(render_template(
            "tdconsole.html", utdsf=utdsf, dio=dio, gbpf=gbpf, message=message, dataRows=data, dateInput=dateInput, clearDate=clearDate))
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
        return render_template("tdconsole.html", utdsf=utdsf, dio=dio, gbpf=gbpf, message=message, dataRows=data, dateInput=dateInput, clearDate=clearDate)

    else:
        startDatetime = datetime.datetime.now() - datetime.timedelta(days=(datetime.datetime.now().weekday() + 7))
        endDatetime = startDatetime + datetime.timedelta(days=40)
        data = algoSesh.getAssignments(startDatetime, endDatetime)
        return render_template("tdconsole.html", utdsf=utdsf, dio=dio, gbpf=gbpf, message=message, dataRows=data, dateInput=dateInput, clearDate=clearDate)


@app.route("/tdstats", methods=['POST', 'GET'])
def tdstats():
    avgTakedowns = dbSession.getAverageTdScore()
    avgPenalty = dbSession.getAveragePenaltyScore()
    emailInputForm = emailInput()

    if emailInputForm.validate_on_submit():
        userEmail = emailInputForm.email.data
        uid = dbSession.getUid(userEmail)
        pname = dbSession.getPname(uid)
        tdScore = dbSession.getTakedownScore(uid)
        penaltyScore = dbSession.getPenaltyBalance(uid)
        userPenalties = dbSession.getPenalties(uid)
        user = [pname, tdScore, penaltyScore, userPenalties]
        resp = make_response(render_template(
        "tdstats.html", user=user, emailInput=emailInputForm, avgTakedowns=avgTakedowns, avgPenalty=avgPenalty))
        resp.set_cookie("userEmail", userEmail)
        return resp

    try:
        userEmail = request.cookies.get("userEmail")
        uid = dbSession.getUid(userEmail)
        pname = dbSession.getPname(uid)
        tdScore = dbSession.getTakedownScore(uid)
        penaltyScore = dbSession.getTakedownScore(uid)
        userPenalties = dbSession.getPenalties(uid)
        user = [pname, tdScore, penaltyScore, userPenalties]
    except Exception:  # Likely if user email doesn't exist
        user = [None]

    return render_template("tdstats.html", user=user, emailInput=emailInputForm, avgTakedowns=avgTakedowns, avgPenalty=avgPenalty)
