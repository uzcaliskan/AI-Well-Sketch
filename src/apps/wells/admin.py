from django.contrib import admin

from .models import Event, Well, WellName

admin.site.register(Well)
admin.site.register(WellName)
admin.site.register(Event)
