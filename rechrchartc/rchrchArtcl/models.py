from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

class Admins(models.Model):
    """
    Modèle représentant un administrateur dans la base de données.

    Champs :
    - `id` : Clé primaire automatiquement générée.
    - `name` : Nom de l'administrateur.
    - `password` : Mot de passe de l'administrateur.

    Méthodes :
    - Aucune méthode spécifique définie dans ce modèle.

    Exemple d'utilisation :
    ```python
    # Création d'un nouvel administrateur
    new_admin = Admins.objects.create(
        name="admin_user",
        password="secure_password123",
    )
    ```
    """
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255,unique=True)
    password = models.CharField(max_length=255)

class Moderateurs(models.Model):
    """
    Modèle représentant un modérateur dans la base de données.

    Champs :
    - `id` : Clé primaire automatiquement générée.
    - `name` : Nom du modérateur.
    - `email` : Adresse e-mail du modérateur.
    - `password` : Mot de passe du modérateur.

    Méthodes :
    - Aucune méthode spécifique définie dans ce modèle.

    Exemple d'utilisation :
    ```python
    # Création d'un nouveau modérateur
    new_moderator = Moderateurs.objects.create(
        name="moderator_user",
        email="moderator@example.com",
        password="secure_password456",
    )
    ```
    """
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255,unique=True)
    email = models.EmailField()
    password = models.CharField(max_length=255)

class Article(models.Model):
     """
    Modèle représentant un article dans la base de données.

    Champs :
    - `id` : Clé primaire automatiquement générée.
    - `titre` : Titre de l'article.
    - `auteurs` : Les auteurs de l'article.
    - `institutions` : Les institutions liées à l'article.
    - `references` : Les références bibliographiques de l'article.
    - `mot_cles` : Les mots-clés associés à l'article.
    - `resume` : Un résumé de l'article.
    - `contenu` : Le contenu principal de l'article.
    - `pdf` : Le chemin vers le fichier PDF associé à l'article.
    - `date_pub` : La date de publication de l'article.

    Méthodes :
    - Aucune méthode spécifique définie dans ce modèle.

    Exemple d'utilisation :
    ```python
    # Création d'un nouvel article
    new_article = Article.objects.create(
        titre="Introduction to Django",
        auteurs="John Doe",
        institutions="Tech University",
        references="Doe, J. (2022). Django: A Comprehensive Guide.",
        mot_cles="Django, Web Development, Beginners",
        resume="Overview of Django's features and usage.",
        contenu="A beginner's guide to Django web framework.",
        pdf="/path/to/django_guide.pdf",
    )
    ```
     """
     id = models.BigAutoField(primary_key=True)
     titre = models.TextField()
     auteurs = models.TextField()
     institutions = models.TextField()
     references = models.TextField()
     mot_cles = models.TextField()
     resume = models.TextField()
     contenu = models.TextField()
     pdf = models.FileField(upload_to='pdfs/')
     date_pub = models.DateField(auto_now_add=True)

class TempModel(models.Model):
    """
    Modèle temporaire représentant un fichier PDF téléchargé.

    Champs :
    - `pdf` : Le fichier PDF téléchargé.

    Méthodes :
    - Aucune méthode spécifique définie dans ce modèle.

    Exemple d'utilisation :
    ```python
    # Création d'une nouvelle instance TempModel
    temp_model_instance = TempModel.objects.create(
        pdf="/path/to/temporary_file.pdf",
    )
    ```
    """
    pdf = models.FileField(upload_to='temp_pdfs/')

     
class User(AbstractUser):
    """
    Modèle personnalisé d'utilisateur héritant d'AbstractUser.

    Champs :
    - `id` : Clé primaire automatiquement générée.
    - `name` : Nom de l'utilisateur.
    - `password` : Mot de passe de l'utilisateur.
    - `favoris` : Relation ManyToMany avec les articles marqués comme favoris.

    Méthodes :
    - Aucune méthode spécifique définie dans ce modèle.

    Exemple d'utilisation :
    ```python
    # Création d'un nouvel utilisateur
    new_user = User.objects.create(
        name="john_doe",
        password="secure_password789",
    )
    ```
    """
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
    """
    Fonction de signal pour supprimer le fichier associé à l'instance TempModel lors de la suppression de l'objet.
    """
     # Pass False so FileField doesn't save the model
    instance.pdf.delete(False)
@receiver(pre_delete, sender=Article)
def delete_file_on_object_delete(sender, instance, **kwargs):
    """
    Fonction de signal pour supprimer le fichier associé à l'instance Article lors de la suppression de l'objet.
    """
     # Pass False so FileField doesn't save the model
    instance.pdf.delete(False)

     


# Create your models here.
