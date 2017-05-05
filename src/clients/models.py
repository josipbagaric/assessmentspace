from django.db import models
from tenant_schemas.models import TenantMixin
from tinymce.models import HTMLField
from django.conf import settings
from datetime import datetime

PLAN_CHOICES = [ (plan['name'], plan['name'] + ' - ' + str(int(plan['price_cents']/100)) + ' EUR/' + plan['per']) for plan in settings.STRIPE_PLANS ]
PLAN_CHOICES.append(('Trial', 'Trial - 30 days'))

YEARS_CHOICES = tuple((str(datetime.now().year + i), str(datetime.now().year + i)) for i in range(20))

MONTHS_CHOICES = tuple((month, month) for month in [
    'January', 
    'February', 
    'March', 
    'April', 
    'May', 
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December'
])

class Client(TenantMixin):

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-created',)
        permissions = (
            ('view_client', 'Can view Client'),
            ('modify_client', 'Can modify Client'),
        )

    name = models.CharField(null=False, unique=True, max_length=100, verbose_name='Company name')
    description = HTMLField(blank=True, verbose_name='Description')
    plan = models.CharField(
        max_length=100,
        null=False,
        choices=PLAN_CHOICES,
        verbose_name='Plan',
    )
    paid_until =  models.DateField()
    on_trial = models.BooleanField()

    created = models.DateTimeField(auto_now_add=True, verbose_name='Created on')
    updated = models.DateTimeField(auto_now=True, verbose_name='Last updated')

### SUBSCRIPTION
class Card(models.Model):

    def __str__(self):
        return ' '.join([
            self.client.first_name, 
            self.client.last_name, 
            ' - ***' + self.card_number[-4:]
        ])

    client = models.ForeignKey(Client, null=True, related_name='cards', on_delete=models.CASCADE)

    card_number = models.CharField(null=False, unique=True, max_length=20, verbose_name="Card Number")
    card_cvv = models.CharField(null=False, max_length=4, verbose_name="Card CVV")
    card_expiry_month = models.CharField(
        max_length=100,
        null=False,
        choices=MONTHS_CHOICES,
        verbose_name='Expiry Month',
    )
    card_expiry_year = models.CharField(
        max_length=100,
        null=False,
        choices=YEARS_CHOICES,
        verbose_name='Expiry Year',
    )