import httplib2
import os
import oauth2client
from oauth2client import client, tools, file
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apiclient import errors, discovery
from dateutil.parser import parse
import requests
import app.db as db
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/gmail.send','https://www.googleapis.com/auth/gmail.settings.basic']
CLIENT_SECRET_FILE = './app/mail/keyfile.json'
APPLICATION_NAME = 'Gmail API Python Send Email'

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'takedowns-email-send.json')
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def SendMessage(to, subject, msgHtml, msgPlain):
    """Sends the given user a message from my UpRight Law email.
    Keyword arguments:
    to -- str
    subject -- str
    msgHtml -- str
    msgPlain -- str
    """
    # [DEBUG]
    to = "jschmitz2@hawk.iit.edu"
    sender = "jschmitz2@hawk.iit.edu"
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    message1 = CreateMessage(sender, to, subject, msgHtml, msgPlain)
    SendMessageInternal(service, "me", message1)

    # print("SENDING MAIL TO jschmitz+test729@uprightlaw.com")

def SendMessageInternal(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)

def CreateMessage(sender, to, subject, msgHtml, msgPlain):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg.attach(MIMEText(msgPlain, 'plain'))
    msg.attach(MIMEText(msgHtml, 'html'))
    raw = base64.urlsafe_b64encode(msg.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}
    return body


def TakedownTradeMessage(uid, dateId, traders):
    debug = 1
    url = ['104.194.115.143', 'localhost'][debug]
    dbSession = db.Session()
    curMeal = dbSession.getCurMealDateId()
    token = dbSession.getSwapKey()
    uname = dbSession.getPname(uid)
    tid = dbSession.getTid(dateId)
    date = parse(dbSession.getIsoDate(dateId))
    meal = ["Lunch", "Dinner"][tid % 2]
    weekday = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"][date.weekday()]
    subject = f"Trade Requested - {weekday} {meal} for {uname}"
    _meal = meal
    for trader in traders:
        traderName = dbSession.getPname(trader)
        traderMeals = dbSession.getUserAssignments(trader)
        tradeLinks = "<ul>"
        for meal in traderMeals:
            if meal[0] < curMeal:
                continue
            tradeMealTid = dbSession.getTid(meal[0])
            tradeMealDateTime = dbSession.getIsoDate(meal[0])
            purchaseUrl = ""
            mealtime = ["Lunch", "Dinner"][tradeMealTid % 2]
            day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"][int((tradeMealTid - tradeMealTid % 2)/2)]

            if tradeMealTid in dbSession.getUserAvailibility(uid):
                payload = {
                    "mode": "trade",
                    "uid": uid,
                    "mealDateId": dateId,
                    "tradeDateId": meal[0],
                    "tradeUid": trader,
                    "token": token
                }
                r = requests.Request('GET', 'http://104.194.115.143:5000/tdtrade', params=payload).prepare()
                tradeLinks += f"<li><strong>{day} {mealtime}, {tradeMealDateTime[:10]}:</strong> {r.url}"

        tradeLinks += "</ul>"
        payload = {
            "mode": "purchase",
            "uid": uid,
            "mealDateId": dateId,
            "tradeUid": trader,
            "token": token
        }
        r = requests.Request('GET', 'http://104.194.115.143:5000/tdtrade', params=payload).prepare()
        purchaseUrl = r.url
        mealDateTime = dbSession.getIsoDate(dateId)
        message = f"""
        <h3>{traderName},<h3>

        <p>{uname} is looking to trade their {weekday} {_meal} takedown, on {mealDateTime[:10]}.</p>
        <br>
        <p>Please click a link below to trade for that takedown.</p>"""
        message += "<h5>Tradeable Takedowns:</h5>"
        message += tradeLinks
        message += "<h5>Alternatively, you can take the takedown and recieve a credit.<h5>"
        message += f"{purchaseUrl}"
        message += "<p><br>With a cold, mechanical heart,<br><i>The Takedowns Automation Project</i></p>"

        rEmail = dbSession.getEmail(trader)
        SendMessage(rEmail, subject, message, message)




def main():
    to = "jschmitz2@hawk.iit.edu"
    subject = "Test Email"
    msgHtml = "Hi<br/>Html Email"
    msgPlain = "Hi\nPlain Email"
    SendMessage(to, subject, msgHtml, msgPlain)

if __name__ == '__main__':
    main()
