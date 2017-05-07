from django.shortcuts import render
from django.conf import settings

from .forms import ContactForm
from util.emails import send_contact_email

def index(request):

    context = {
        'sent': False,
        'is_demo': settings.__dict__.get('DEMO', False),
    }

    if request.method == "POST":        

        form = ContactForm(request.POST)

        if form.is_valid():
            send_contact_email(form)            
            context['sent'] = True
        else:
            context['errors'] = form.errors

    else:
        form = ContactForm()
    
    context['form'] = form

    return render(request, 'index.html', context)