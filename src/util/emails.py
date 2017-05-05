from django.core.mail import EmailMessage

from app.settings import EMAIL_HOST_USER

def send_contact_email(form):

    subject = 'You have a new contact!'

    body = """
name = {}
email = {}
company = {}
question = {}
heard_about = {}""".format(
    form['name'].data, 
    form['email'].data, 
    form['company'].data, 
    form['question'].data,
    form['heard_about'].data, 
)    
    
    email = EmailMessage(
        subject, 
        body, 
        to=[EMAIL_HOST_USER]
    )
    email.send()