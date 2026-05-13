from flask_wtf import FlaskForm
from flask_wtf.recaptcha import validators
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField
from wtforms.validators import NumberRange
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, Length, IPAddress

class DeviceDiscoveryForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2,max=30)])
    password = PasswordField('Password', validators=[DataRequired()])
    ip_network = StringField('IP-Network (like 192.168.1.0/24)', validators=[DataRequired()])
    telnet = BooleanField('Enable Telnet discovery if no SSH answer')
    jumphost = SelectField('Jumphost (optional)', choices=[('none', '-- Direct Connection --')])
    submit = SubmitField('Start Discovery')

class JumphostForm(FlaskForm):
    name = StringField('Name / Label', validators=[DataRequired(), Length(min=1, max=50)])
    ip_addr = StringField('IP Address', validators=[DataRequired()])
    port = IntegerField('SSH Port', default=22, validators=[DataRequired(), NumberRange(min=1, max=65535)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=30)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Add Jumphost')

class QuickCommand(FlaskForm):
    commands = TextAreaField('Quickcommands ', validators=[DataRequired()])
    config = BooleanField('Configuration Commands')
    submit = SubmitField('Execute Commands')

class PasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Import Devices')
