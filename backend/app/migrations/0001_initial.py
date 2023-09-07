# Generated by Django 4.2.5 on 2023-09-07 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DefensePercent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('defenspercent_text', models.CharField(max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Top',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('top_text', models.CharField(max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='TravelDays',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('yeardays_text', models.CharField(max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='YearCalendar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('yearcalendar_text', models.CharField(max_length=4)),
            ],
        ),
    ]
