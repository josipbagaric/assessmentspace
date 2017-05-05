from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def support(request):

    return render(
        request,
        'support/support.html',
        context={}
    )
