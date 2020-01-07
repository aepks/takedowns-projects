from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, DecimalField
from wtforms.validators import DataRequired, Regexp, ValidationError
import app.db as db


class DateInput(FlaskForm):
    startDate = StringField(
        "Start Date (MM/DD)", validators=[DataRequired(), Regexp(r"^[0-9]{2}/[0-9]{2}$")])
    endDate = StringField(
        "End Date (MM/DD)", validators=[DataRequired(), Regexp(r"^[0-9]{2}/[0-9]{2}$")])
    submit = SubmitField("Submit Request")


class ClearDate(FlaskForm):
    resetDate = StringField(
        "Start Date (MM/DD)", validators=[DataRequired(), Regexp(r"^[0-9]{2}/[0-9]{2}$")])
    endResetDate = StringField(
        "End Reset (MM/DD) (Opt.)", validators=[Regexp(r"^[0-9]{2}/[0-9]{2}$")])
    # lunchDinner = RadioField(
    #     "Meal Choice", choices=[("l", "Lunch"), ("d", "Dinner"), ("b", "Both")])
    submit = SubmitField("Submit Request")


class GoodBoyPointForm(FlaskForm):
    def checkEmail(form, field):
        dbSession = db.Session()
        if dbSession.testEmail(field.data):
            return True
        else:
            raise ValidationError("Email entered is not valid.")

    email = StringField("Email Address", validators=[
                        DataRequired(), checkEmail])
    points = DecimalField("Points Awarded", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    submit = SubmitField("Submit Request")


class emailInput(FlaskForm):
    def checkEmail(form, field):
        dbSession = db.Session()
        if dbSession.testEmail(field.data):
            return True
        else:
            raise ValidationError("Email entered is not valid.")

    email = StringField("Email Address", validators=[
                        DataRequired(), checkEmail])
    submit = SubmitField("Submit Request")
