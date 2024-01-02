from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

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
     auteurs = models.CharField(max_length=255)
     institutions = models.CharField(max_length=255)
     references = models.TextField()
     mot_cles = models.CharField(max_length=255)
     resume = models.TextField()
     contenu = models.TextField()
     pdf = models.FileField(upload_to='pdfs/')
     date_pub = models.DateField(auto_now_add=True)

class TempModel(models.Model):
     pdf = models.FileField(upload_to='temp_pdfs/')

     
class User(AbstractUser):
     id = models.BigAutoField(primary_key=True)
     name = models.CharField(max_length=255, unique=True)
     password = models.CharField(max_length=255)
     favoris = models.ManyToManyField(Article)
     username = None 
     last_login = None 
     REQUIRED_FIELDS = []
     USERNAME_FIELD = "name"

@receiver(pre_delete, sender=TempModel)
def delete_file_on_object_delete(sender, instance, **kwargs):
     # Pass False so FileField doesn't save the model
     instance.pdf.delete(False)
@receiver(pre_delete, sender=Article)
def delete_file_on_object_delete(sender, instance, **kwargs):
     # Pass False so FileField doesn't save the model
     instance.pdf.delete(False)

     


# Create your models here.
