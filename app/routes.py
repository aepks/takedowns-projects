from app import app
from flask import request, render_template, make_response, redirect, url_for
from app.forms import DateInput, UpdateTakedownsSheet, ClearDate, GoodBoyPointForm, emailInput
import app.algo as algo
import app.db as db
import datetime

algoSesh = algo.Session()
dbSession = db.Session()


@app.route("/", methods=['POST', 'GET'])
@app.route("/tdconsole", methods=['POST', 'GET'])
def tdconsole():
    algoSesh.readResponseForms()
    algoSesh.readPenalties()

    dateInput = DateInput()
    clearDate = ClearDate()
    gbpf = GoodBoyPointForm()
    utdsf = UpdateTakedownsSheet()

    message = None

    if gbpf.validate_on_submit():
        email = gbpf.email.data
        points = gbpf.points.data
        description = gbpf.description.data
        algoSesh.awardGoodBoyPoint(email, points, description)
        message = f"Awarded {points} to {email}."
        return redirect(url_for('.tdconsole'))

    if clearDate.validate_on_submit():
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

    if dateInput.validate_on_submit():
        startDate = dateInput.startDate.data + "/2020"
        endDate = dateInput.endDate.data + "/2020"
        startDatetime = datetime.datetime.strptime(startDate, "%m/%d/%Y")
        endDatetime = datetime.datetime.strptime(
            endDate, "%m/%d/%Y") + datetime.timedelta(days=1)
        data = algoSesh.getAssignments(startDatetime, endDatetime)
        resp = make_response(render_template(
            "tdconsole.html", utdsf=utdsf, gbpf=gbpf, message=message, dataRows=data, dateInput=dateInput, clearDate=clearDate))
        resp.set_cookie("startDate", startDate)
        resp.set_cookie("endDate", endDate)
        return resp

    if utdsf.validate_on_submit():
        algoSesh.updateTakedowns()


    if "startDate" in request.cookies:
        startDate = request.cookies.get("startDate")
        endDate = request.cookies.get("endDate")
        startDatetime = datetime.datetime.strptime(startDate, "%m/%d/%Y")
        endDatetime = datetime.datetime.strptime(
            endDate, "%m/%d/%Y") + datetime.timedelta(days=1)
        data = algoSesh.getAssignments(startDatetime, endDatetime)
        return render_template("tdconsole.html", utdsf=utdsf, gbpf=gbpf, message=message, dataRows=data, dateInput=dateInput, clearDate=clearDate)

    else:
        startDatetime = datetime.datetime(day=15, month=1, year=2020)
        endDatetime = startDatetime + datetime.timedelta(days=10)
        data = algoSesh.getAssignments(startDatetime, endDatetime)
        return render_template("tdconsole.html", utdsf=utdsf, gbpf=gbpf, message=message, dataRows=data, dateInput=dateInput, clearDate=clearDate)


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

    if "userEmail" not in request.cookies:
        user = [None]
    else:
        userEmail = request.cookies.get("userEmail")
        uid = dbSession.getUid(userEmail)
        pname = dbSession.getPname(uid)
        tdScore = dbSession.getTakedownScore(uid)
        penaltyScore = dbSession.getTakedownScore(uid)
        userPenalties = dbSession.getPenalties(uid)
        user = [pname, tdScore, penaltyScore, userPenalties]
    return render_template("tdstats.html", user=user, emailInput=emailInputForm, avgTakedowns=avgTakedowns, avgPenalty=avgPenalty)
