from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField
from wtforms.validators import DataRequired, Email, ValidationError


class UrlForm(FlaskForm):
    url = StringField("url", validators=[DataRequired()])

    def validate_url(self, url):
        if '/dp/' not in str(url):
            raise ValidationError("Unable to fetch the product from Amazon, please provide full url.")


class AlertForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    price = DecimalField('Amount', validators=[DataRequired()])
    submit = SubmitField('Submit')