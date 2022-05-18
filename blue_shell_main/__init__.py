import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

ENV = 'dev'
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('AMAZON_PT')
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://jlpkqknyooazfh:28899e74eb97bae622968a525227ea5eff1d17e7609bcb6b0cb6dfbbe295b04c@ec2-44-194-4-127.compute-1.amazonaws.com:5432/d2bm97rqttpal2'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('BSA_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('BSA_PW')
mail = Mail(app)

db = SQLAlchemy(app)

from blue_shell_main import routes