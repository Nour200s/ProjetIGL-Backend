from django.db import models
from django.contrib.auth.models import AbstractUser

class Admins(models.Model):
     id = models.BigAutoField(primary_key=True)
     name = models.CharField(max_length=255,unique=True)
     password = models.CharField(max_length=255)

class Moderateurs(models.Model):
     id = models.BigAutoField(primary_key=True)
     name = models.CharField(max_length=255,unique=True)
     password = models.CharField(max_length=255)

class Article(models.Model):
     id = models.BigAutoField(primary_key=True)
     titre = models.CharField(max_length=255)
     resume = models.TextField()
     contenu = models.TextField()
     pdf = models.TextField()

class User(AbstractUser):
     id = models.BigAutoField(primary_key=True)
     name = models.CharField(max_length=255, unique=True)
     password = models.CharField(max_length=255)
     favoris = models.ManyToManyField(Article)
     username = None 
     last_login = None 
     REQUIRED_FIELDS = []
     USERNAME_FIELD = "name"

class Institution(models.Model):
     id = models.BigAutoField(primary_key=True)
     nom = models.CharField(max_length=255)
     adresse = models.CharField(max_length=255)


class Auteurs(models.Model):
     id = models.BigAutoField(primary_key=True)
     institutions = models.ForeignKey(Institution,on_delete=models.CASCADE)
     nom = models.CharField(max_length=255)
     email = models.CharField(max_length=255)
     articles = models.ManyToManyField(Article)

class References(models.Model):
     id = models.BigAutoField(primary_key=True)
     article = models.ForeignKey(Article ,on_delete=models.CASCADE)
     contenu = models.CharField(max_length=512)


     


# Create your models here.
