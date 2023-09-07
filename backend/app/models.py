from django.db import models

class Top(models.Model):
    top_text = models.CharField(max_length=4)

    def __str__(self):
        return self.top_text

class DefensePercent(models.Model):
    defenspercent_text = models.CharField(max_length=3)

    def __str__(self):
        return self.defenspercent_text

class YearCalendar(models.Model):
    yearcalendar_text = models.CharField(max_length=4)

    def __str__(self):
        return self.yearcalendar_text

class TravelDays(models.Model):
    yeardays_text = models.CharField(max_length=4)

    def __str__(self):
        return self.yeardays_text