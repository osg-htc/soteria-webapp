from flask_wtf import FlaskForm
from wtforms import SelectField, SelectMultipleField, StringField, \
    TimeField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, \
    Regexp, NumberRange, InputRequired, URL
from registry.util import get_fresh_desk_api

requirement_choices = [
    ("", "Select Requirement Met"),
    ("a-xrac", "Active XRAC allocation."),
    ("b-listed-and-published", "Institute Member and Recently Published"),
    ("c-active-grant-on-ORCID", "Active Federal Grant on ORCID Profile"),
    ("d-institution-non-R1-HBCU-TCU", "Non R1, HBCU, or TCU institute member"),
    ("e-pi-approval", "SOTERIA PI approval")
]


class ResearcherApprovalForm(FlaskForm):
    email = StringField("Institute Affiliated Email", validators=[InputRequired()])
    criteria = SelectField("Requirement Met", choices=requirement_choices, validators=[InputRequired()])

    b_website_url = StringField("Website URL", validators=[URL(), InputRequired()])
    b_publication_doi = StringField("Publication DOI", validators=[InputRequired()])

    c_grant_number = StringField("Grant Number", validators=[InputRequired()])
    c_funding_agency = StringField("Funding Agency", validators=[InputRequired()])

    d_website_url = StringField("Website URL", validators=[URL(), InputRequired()])
    d_classification = StringField("Institution Classification", validators=[InputRequired()])

    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.a_fields = []
        self.b_fields = [self.b_website_url, self.b_publication_doi]
        self.c_fields = [self.c_grant_number, self.c_funding_agency]
        self.d_fields = [self.d_website_url, self.d_classification]
        self.e_fields = []


    class Meta:
        csrf = False  # CSRF not needed because no data gets modified

    def validate(self):

        self.email.validate(self)

        if not self.criteria.validate(self):
            return False

        # Validate that the requirements are met for the selected criteria
        criteria_fields = self.get_criteria_fields()
        return all(field.validate(self) for field in criteria_fields)

    def get_criteria_fields(self):
        if self.criteria.data == "b-listed-and-published":
            return self.b_fields

        if self.criteria.data == "c-active-grant-on-ORCID":
            return self.c_fields

        if self.criteria.data == "c-active-grant-on-ORCID":
            return self.d_fields

        return []

    def submit_request(self):
        api = get_fresh_desk_api()
        selected_requirement = next(x[1] for x in requirement_choices if x[0] == self.criteria.data)
        description = f"""
            <div>
              <p>
                Researcher has selected that they meet requirement: {selected_requirement}
              </p>
            """
        for field in self.get_criteria_fields():
            description += f"""
                <h5>
                    {field.label.text}
                </h5>
                <p>
                    {field.data}
                </p>
            """
        description += "</div>"

        ticket = {
            "name": "TODO LAST",
            "email": self.email.data,
            "subject": "SOTERIA Researcher Application",
            "description": description,
            "group_id": 12000006916,
            "priority": 2,
            "status": 2,
            "type": "SOTERIA Researcher Application"
        }

        a = api.create_ticket(**ticket)
