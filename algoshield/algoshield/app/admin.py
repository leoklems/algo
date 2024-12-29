from django.contrib import admin
from .models import Account, Building, Appartment, Customer

admin.site.register(Account)
admin.site.register(Building)
admin.site.register(Appartment)
admin.site.register(Customer)
# admin.site.register(User)
# admin.site.register(Feedback)