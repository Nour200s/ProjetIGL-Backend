from django.db import models

class Admins(models.Model):
     id = models.BigAutoField(primary_key=True)
     name = models.CharField(max_length=255)
     password = models.CharField(max_length=255)

class Moderateurs(models.Model):
     id = models.BigAutoField(primary_key=True)
     name = models.CharField(max_length=255)
     password = models.CharField(max_length=255)

class Article(models.Model):
     id = models.BigAutoField(primary_key=True)
     titre = models.CharField(max_length=255)
     resume = models.TextField()
     contenu = models.TextField()
     pdf = models.TextField()

class User(models.Model):
     id = models.BigAutoField(primary_key=True)
     name = models.CharField(max_length=255)
     password = models.CharField(max_length=255)
     favoris = models.ManyToManyField(Article)

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
