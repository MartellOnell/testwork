from django.contrib import admin

from .models import TravelDays, YearCalendar, DefensePercent, Top

admin.site.register(Top)
admin.site.register(TravelDays)
admin.site.register(DefensePercent)
admin.site.register(YearCalendar)