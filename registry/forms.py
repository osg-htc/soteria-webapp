from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextField, SubmitField
from wtforms.validators import InputRequired
from wtforms.fields.html5 import EmailField
from wtforms.csrf.session import SessionCSRF

class BaseForm(FlaskForm):
    class Meta:
        csrf = False

class ResearcherApplication(BaseForm):

    email = EmailField("University/Institute Linked Email")
    criteria = SelectField("Application Criteria Met", choices=[
        ("active-xrac", "You have a active XRAC allocation"),
        ("website-recent-publication", "Website Listing and Recent Publication"),
        ("active-US-grant", "Active Federal US Grant through Institution"),
        ("website-classification", "Website Listing and non-R1, HBCU, or TCU"),
        ("soteria-pi-approval", "Approved by a Soteria PI")
    ], validators=[InputRequired()])

    submit = SubmitField("Submit Application")