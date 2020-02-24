from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, DecimalField, SelectField, PasswordField
from wtforms.validators import DataRequired, Regexp, ValidationError
import app.db as db


class DateInput(FlaskForm):
    startDate = StringField(
        "Start Date (MM/DD)", validators=[DataRequired(), Regexp(r"^[0-9]{2}/[0-9]{2}$")])
    endDate = StringField(
        "End Date (MM/DD)", validators=[DataRequired(), Regexp(r"^[0-9]{2}/[0-9]{2}$")])
    submit = SubmitField("Submit Request")


class SolveDateForm(FlaskForm):
    resetDate = StringField(
        "Start Date (MM/DD)", validators=[DataRequired(), Regexp(r"^[0-9]{2}/[0-9]{2}$")])
    endResetDate = StringField(
        "End Reset (MM/DD) (Opt.)", validators=[Regexp(r"^[0-9]{2}/[0-9]{2}$")])
    # lunchDinner = RadioField(
    #     "Meal Choice", choices=[("l", "Lunch"), ("d", "Dinner"), ("b", "Both")])
    submit = SubmitField("Submit Request")


class GoodBoyPointForm(FlaskForm):
    dbSession = db.Session()
    users = dbSession.getUsers()

    email = SelectField("User", choices=users, validators=[DataRequired()])
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

class UpdateTakedownsSheet(FlaskForm):
    password = PasswordField("What's the password?")
    submit = SubmitField("Update Takedowns Sheet")

class DefaultInstacartOrderForm(FlaskForm):
    password = PasswordField("What's the password?")
    submit = SubmitField("Add Default Items")
