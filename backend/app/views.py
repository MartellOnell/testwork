from django.shortcuts import render
from django.http import JsonResponse

from .models import Top, TravelDays, DefensePercent, YearCalendar

def index(req):
    top = Top.objects.get(pk=1).top_text
    percent = DefensePercent.objects.get(pk=1).defenspercent_text
    yearcalendar = YearCalendar.objects.get(pk=1).yearcalendar_text
    traveldays = TravelDays.objects.get(pk=1).yeardays_text
    return JsonResponse({
                "top": top, 
                "percent": percent,
                "yearcalendar": yearcalendar,
                "traveldays": traveldays
            })