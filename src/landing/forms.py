from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, Submit, HTML, Row, Column

HEARD_ABOUT_CHOICES = [
    "Personal referral",
    "Google",
    "Other"
]

class ContactForm(forms.Form):

    name = forms.CharField(required=True, max_length=50)
    email = forms.EmailField(required=True, max_length=100)
    company = forms.CharField(required=False, max_length=50)
    question = forms.CharField(widget=forms.Textarea, required=True)
    heard_about = forms.ChoiceField(
        label='How did you hear about us?',
        choices=[(choice, choice) for choice in HEARD_ABOUT_CHOICES],
    )

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'name',
                    css_class="col-md-6"
                ),
                Column(
                    'email',
                    css_class="col-md-6"
                )
            ),
            Row(
                Column(
                    'company',
                    css_class="col-md-6"
                ),
                Column(
                    'heard_about',
                    css_class="col-md-6"
                )
            ),
            'question',
            Row(
                Column(
                    Submit('submit','Send', css_class="btn-block btn-lg"),
                    css_class="col-md-3 mx-auto"
                )
            ),
        ) 
    