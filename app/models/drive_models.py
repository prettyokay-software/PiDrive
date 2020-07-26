# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>, Matt Hogan <matt@twintechlabs.io>

from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators, PasswordField, BooleanField, IntegerField
from app import db
from app.utils.forms import MultiCheckboxField


class Drive(db.Model):
    __tablename__ = 'drives'
    id = db.Column(db.Integer(), primary_key=True, unique=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(999), nullable=True)
    path = db.Column(db.String(999), nullable=False)
    size = db.Column(db.Integer(), nullable=False)
    free_space = db.Column(db.Integer(), nullable=True)
    mounted = db.Column(db.Boolean(), nullable=False)
    date_created = db.Column(db.DateTime(), nullable=False)
    last_used = db.Column(db.DateTime(), nullable=True)

# Define the Role data model
class DriveLog(db.Model):
    __tablename__ = 'drivelog'
    id = db.Column(db.Integer(), primary_key=True, unique=True)
    drive_id = db.Column(db.Integer(), db.ForeignKey('drives.id', ondelete='CASCADE'))
    action = db.Column(db.String(255), nullable=False)
    data = db.Column(db.Text(), nullable=True)
    user = db.Column(db.Text(), nullable=False)
    action_date = db.Column(db.DateTime(), nullable=False)


# Define the User registration form
# It augments the Flask-User RegisterForm with additional fields
#class MyRegisterForm(RegisterForm):
#    first_name = StringField('First name', validators=[ validators.DataRequired('First name is required')])
#    last_name = StringField('Last name', validators=[ validators.DataRequired('Last name is required')])


# Define the User profile form
#class UserProfileForm(FlaskForm):
#    first_name = StringField('First name', validators=[])
#    last_name = StringField('Last name', validators=[])
#    email = StringField('Email', validators=[validators.DataRequired('Last name is required')])
#    password = PasswordField('Password', validators=[])
#    roles = MultiCheckboxField('Roles', coerce=int)
#    active = BooleanField('Active')
#    submit = SubmitField('Save')



# Define the USB Drive form
class DriveForm(FlaskForm):
    name = StringField('Drive Name', validators=[validators.DataRequired('Drive name is required')])
    description = StringField('Description')
    path = StringField('Drive Image Storage Location', validators=[validators.DataRequired('A path is required')])
    size = IntegerField('Drive Size (GB)', validators=[validators.DataRequired('A drive size is required')])
    save = SubmitField('Save')
