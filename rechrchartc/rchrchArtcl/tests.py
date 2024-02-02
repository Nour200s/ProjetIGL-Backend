from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Moderateurs ,User
from .models import Article
from .views import ModeratorUpdate


class ArticleViewsetTestCase(TestCase):
    def setUp(self):
        # Créer un objet Article pour le test
        self.article = Article.objects.create(
           titre = "Introduction to Python Programming",
           auteurs = "John Doe, Jane Smith",
           contenu = "This is a beginner-friendly guide to Python programming.",
           resume = "A brief overview of Python and its key features.",
           references = "Doe, J., Smith, J. (2022). Python Programming: A Comprehensive Guide.",
           pdf = "/path/to/python_guide.pdf",
           institutions = "Tech University, Python Learning Center",
           mot_cles = "Python, Programming, Beginners, Tutorial",
        )

        self.data = {
                'name' : 'test',
                'email' : 'test@gmail.com',
                'password' : 'test123',
                    }
        
        # Configurer le client de l'API pour effectuer des requêtes
        self.client = APIClient()


    def testSignIn(self):
         # Créer un utilisateur avec les données définies
        utilisateur = User.objects.create(**self.data)

        # Récupérer le nom de l'utilisateur 'nom est unique'
        nom = utilisateur.name

        # Vérifier si le nom de l'utilisateur correspond à celui défini dans self.data
        self.assertEqual(nom, self.data['name'])    

    
    def testDeleteModerator(self): 
        
        
        # Créer un modérateur pour effectuer la suppression
        moderator = Moderateurs.objects.create(name='test1',email='test@gmail.com',password='test123')
        # Effectuer une requête DELETE pour supprimer le modérateur
        response = self.client.delete(f'/recharchartc/recharchArtcl/api/moderateurs/{self.moderator.id}/')

        # Vérifier si la suppression du modérateur a réussi (statut HTTP 204 No Content)
        self.assertEqual(response.status_code, 204)

        # Vérifier si le modérateur a été supprimé de la base de données
        self.assertFalse(Moderateurs.objects.filter(id=moderator.id).exists())



    def test_patch_article(self):
        """
        Test de mise à jour partielle d'un article via une requête PATCH.

        Objectif du test :
        - Vérifier que la requête PATCH met à jour correctement les champs spécifiés de l'article.

        Étapes du test :
        1. Créer un objet Article.
        2. Effectuer une requête PATCH pour mettre à jour certains champs de l'article.
        3. Vérifier que la requête renvoie un code de statut 200 (OK).
        4. Actualiser l'objet article depuis la base de données.
        5. Vérifier que les champs mis à jour correspondent aux nouvelles données.

        Cette méthode de test vise à garantir que la fonctionnalité de mise à jour partielle des articles fonctionne correctement.
        """
        new_data = {
             "titre": "Advanced Python Techniques",
             "contenu": "Exploring advanced concepts and techniques in Python programming.",
             "resume": "A detailed exploration of advanced Python features for experienced developers.",
        }

        # Effectuer une requête PATCH pour mettre à jour l'article
        response = self.client.patch(f'/article/{self.article.id}', new_data, format='json')

        # Vérifier que la réponse est un succès (status code 200 OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Actualiser l'objet article depuis la base de données
        updated_article = Article.objects.get(id=self.article.id)

        # Vérifier que les champs ont été mis à jour correctement
        self.assertEqual(updated_article.titre, new_data["titre"])
        self.assertEqual(updated_article.contenu, new_data["contenu"])
        self.assertEqual(updated_article.resume, new_data["resume"])

