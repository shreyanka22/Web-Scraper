from django.db import models

class PhoneNumber(models.Model):
    num = models.CharField(max_length= 255, primary_key=True)

class Email(models.Model):
    email = models.CharField(max_length = 255, primary_key=True)

class Link(models.Model):
    url = models.CharField(max_length = 255, primary_key=True)

class Site(models.Model):
    url = models.CharField(max_length = 255, primary_key=True)
    last_edited = models.DateTimeField(auto_now=True)
    links = models.ManyToManyField(Link)
    phone_numbers = models.ManyToManyField(PhoneNumber)
    emails = models.ManyToManyField(Email)
