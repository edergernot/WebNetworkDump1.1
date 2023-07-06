from flask_wtf import FlaskForm
from flask_wtf.recaptcha import validators
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, Length, IPAddress

class DeviceDiscoveryForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2,max=30)])
    password = PasswordField('Password', validators=[DataRequired()])
    ip_network = StringField('IP-Network (like 192.168.1.0/24)', validators=[DataRequired()])
    submit = SubmitField('Start Discovery')




