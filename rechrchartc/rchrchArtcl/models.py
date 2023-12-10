from django.db import models

class User(models.Model):
     name = models.CharField(max_length=255)
     password = models.CharField(max_length=255)

# Create your models here.
