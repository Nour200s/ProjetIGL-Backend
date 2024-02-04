from rest_framework.views import APIView 
from .api.serializers import *
from rest_framework.response import Response 

from .models import *
 
from oauth2client.service_account import ServiceAccountCredentials

from rest_framework import status

import PyPDF2
from django.db import connections
from django.http import JsonResponse
from elasticsearch_dsl import Q, Date, Document, Search,Text,Range

from django.shortcuts import HttpResponse
from django.test import TestCase, Client
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
#FOR TEXT EXTRACTION
import fitz 
from .multi_column import column_boxes
import spacy 
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError
from elasticsearch.exceptions import NotFoundError

class Registerview(APIView):
    """
    View for registering a user.

    This view checks if a user with the given name already exists as a User, Moderateur, or Admin.
    If not, it creates a new User using the provided data.

    Attributes:
        None

    Methods:
        post(request): Handles the POST request for user registration.

    Raises:
        None
    """
    def post(self , request): 
        """
        Handle POST request for user registration.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """
        user = User.objects.filter(name=request.data["name"]).first()
        moderateur = Moderateurs.objects.filter(name=request.data["name"]).first()
        admin = Admins.objects.filter(name=request.data["name"]).first()
        if user is None and moderateur is None and admin is None :
            serializer = UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer)
        else:
            return Response({
                "ERROR" : "Not valid"
            })
class Loginview(APIView):
    """ 
     A class-based view for handling user login.

    This view authenticates users, moderators, and administrators based on the provided name and password.
    If the authentication is successful, it returns a token and information about the type of visitor.

    Parameters:
    - `request`: The Django HTTP request object.

    Returns:
    - If authentication is successful:
        - A JSON response containing:
            - "token": The user's name (used as a token for simplicity).
            - "visitor": The type of visitor (user, moderator, or administrator).
            - "Validation": "valid"
    - If authentication fails:
        - A JSON response with "Validation": "Not valid".

    Example Usage:
    ```python
    # Example usage of Loginview
    class SomeView(APIView):
        def some_method(self, request):
            name = request.data["name"]
            password = request.data["password"]

            # Calling Loginview
            login_view = Loginview()
            response = login_view.post(request)

            # Process the response
            if response.data["Validation"] == "valid":
                # Authentication successful
                token = response.data["token"]
                visitor_type = response.data["visitor"]

            else:
                # Authentication failed
    ```
    """
    def post(self , request):
        """
        Handles the POST request for user login.

        Parameters:
        - `request`: The Django HTTP request object.

        Returns:
        - If authentication is successful:
            - A JSON response containing:
                - "token": The user's name (used as a token for simplicity).
                - "visitor": The type of visitor (user, moderator, or administrator).
                - "Validation": "valid"
        - If authentication fails:
            - A JSON response with "Validation": "Not valid".
        """
        name = request.data["name"]
        password = request.data["password"]
        user = User.objects.filter(name=name).first()
        moderateur = Moderateurs.objects.filter(name=request.data["name"]).first()
        admin = Admins.objects.filter(name=request.data["name"]).first()
        visitor = "Not Found"
        if user is not None:
            if  user.password == password :
                visitor = "user"
        elif moderateur is not None :
            if  moderateur.password==password:
                visitor = "moderateur"
        elif admin is not None :
            if  admin.password==password:
                visitor = "administrateur"
        if visitor != "Not Found":
            reponse = Response() 
            reponse.data = {
                "token" : name, 
                "visitor" : visitor , 
                "Validation" : "valid"
            }
            return reponse 
        else: return Response({
            "Validation" : "Not valid"
        })
    

class ModeratorList(APIView):
    """
    A class-based view for retrieving a list of moderators.

    This view handles the GET request and returns a serialized list of all moderators.

    Parameters:
    - `request`: The Django HTTP request object.

    Returns:
    - A JSON response containing the serialized data of all moderators.

    Example Usage:
    ```python
    # Example usage of ModeratorList
    class SomeView(APIView):
        def some_method(self, request):
            # Calling ModeratorList
            moderator_list_view = ModeratorList()
            response = moderator_list_view.get(request)

            # Process the response
            moderators_data = response.data
           
    ```
    """
    def get(self,request):
        """
        Handles the GET request for retrieving a list of moderators.

        Parameters:
        - `request`: The Django HTTP request object.

        Returns:
        - A JSON response containing the serialized data of all moderators.
        """
        mods = Moderateurs.objects.all()
        serializer = ModerateursSerializer(mods,many=True)


        return Response(serializer.data)
    
class ModeratorUpdate(APIView):
    """
    Une vue basée sur les classes pour la mise à jour des modérateurs.

    Cette vue prend en charge les requêtes GET, PUT, DELETE et POST pour la mise à jour et la manipulation des modérateurs.

    Paramètres :
    - `request` : L'objet de requête HTTP Django.
    - `pk` : La clé primaire (ID) du modérateur à manipuler.

    Retours :
    - Pour la requête GET :
        - Une réponse JSON contenant les données sérialisées du modérateur avec l'ID spécifié.
    - Pour la requête PUT :
        - Une réponse JSON contenant les données sérialisées du modérateur mis à jour.
    - Pour la requête DELETE :
        - Une réponse indiquant que le modérateur a été supprimé.
    - Pour la requête POST :
        - Si la création du modérateur est réussie :
            - Une réponse JSON contenant les données sérialisées du nouveau modérateur.
        - Si la création échoue :
            - Une réponse JSON indiquant une erreur avec le message "Not valid".

    Exemple d'utilisation :
    ```python
    # Exemple d'utilisation de ModeratorUpdate
    class SomeView(APIView):
        def some_method(self, request):
            # Exécuter une requête GET pour obtenir les données d'un modérateur
            moderator_update_view = ModeratorUpdate()
            get_response = moderator_update_view.get(request, pk=1)

            # Exécuter une requête PUT pour mettre à jour un modérateur
            put_response = moderator_update_view.put(request, pk=1)

            # Exécuter une requête DELETE pour supprimer un modérateur
            delete_response = moderator_update_view.delete(request, pk=1)

            # Exécuter une requête POST pour créer un nouveau modérateur
            post_response = moderator_update_view.post(request)

           
    ```
    """
    def get(self,request,pk):
        """
        Traite la requête GET pour obtenir les données d'un modérateur.

        Paramètres :
        - `request` : L'objet de requête HTTP Django.
        - `pk` : La clé primaire (ID) du modérateur à récupérer.

        Retours :
        - Une réponse JSON contenant les données sérialisées du modérateur avec l'ID spécifié.
        """
        mods = Moderateurs.objects.get(id=pk)
        serializer = ModerateursSerializer(mods,many=False)
        return Response(serializer.data)
    def put(self,request,pk):
        """
        Traite la requête PUT pour mettre à jour les données d'un modérateur.

        Paramètres :
        - `request` : L'objet de requête HTTP Django.
        - `pk` : La clé primaire (ID) du modérateur à mettre à jour.

        Retours :
        - Une réponse JSON contenant les données sérialisées du modérateur mis à jour.
        """
        data = request.data
        mod = Moderateurs.objects.get(id=pk)
        serializer = ModerateursSerializer(instance=mod ,data=data)

        if serializer.is_valid():
            serializer.save() 
        return Response(serializer.data)
    def delete(self,request,pk):
        """
        Traite la requête DELETE pour supprimer un modérateur.

        Paramètres :
        - `request` : L'objet de requête HTTP Django.
        - `pk` : La clé primaire (ID) du modérateur à supprimer.

        Retours :
        - Une réponse indiquant que le modérateur a été supprimé.
        """
        mod = Moderateurs.objects.get(id=pk)
        mod.delete()
        return Response("Moderateur supprimé")
    def post(self,request):
        """
        Traite la requête POST pour créer un nouveau modérateur.

        Paramètres :
        - `request` : L'objet de requête HTTP Django.

        Retours :
        - Si la création du modérateur est réussie :
            - Une réponse JSON contenant les données sérialisées du nouveau modérateur.
        - Si la création échoue :
            - Une réponse JSON indiquant une erreur avec le message "Not valid".
        """
        user = User.objects.filter(name=request.data["name"]).first()
        moderateur = Moderateurs.objects.filter(name=request.data["name"]).first()
        admin = Admins.objects.filter(name=request.data["name"]).first()
        if user is None and moderateur is None and admin is None :
            newmod = Moderateurs.objects.create(
                name = request.data["name"],
                password = request.data["password"]
            )
            serializer = ModerateursSerializer(newmod ,many=False)
            return Response(serializer)
        else:
            return Response({
                "ERROR" : "Not valid"
            })

class ArticleIndex(Document):
    id = Text()
    title = Text(fields={'raw': Text(index=False)}) 
    sumup = Text()
    content= Text()
    date = Date()
    keywords = Text(multi=True)  
    author = Text()  
    institus = Text(multi=True)
    class Index:
        name = 'articles' 
class ArticleAdd(APIView):
    """
    Une vue basée sur les classes pour ajouter un article à partir d'un fichier PDF.

    Cette vue prend en charge les requêtes POST pour extraire les informations d'un PDF, créer un nouvel article
    dans la base de données Django, et indexer cet article dans Elasticsearch.

    Paramètres :
    - `request` : L'objet de requête HTTP Django.
    - `args` et `kwargs` : Arguments et mots-clés supplémentaires pouvant être passés à la vue.

    Retours :
    - Une réponse indiquant que l'article a été ajouté.

    Méthodes :
    - `extractText(pdf_file: str) -> [str]` : Extrait le texte de toutes les pages d'un fichier PDF.
    - `extract_authors(text: str) -> [str]` : Extrait les noms d'auteurs à partir du texte en utilisant spaCy.
    - `extract_organizations(text: str) -> [str]` : Extrait les organisations à partir du texte en utilisant spaCy.
    - `extract(text: str, start_word: str, end_word: str) -> str` : Extrait le texte entre deux mots-clés spécifiés.
    - `extract_to(text: str, end_word: str) -> str` : Extrait le texte jusqu'à un mot-clé spécifié.
    - `extract_infos(pdf_name: str) -> Tuple[str, str, str, str, str, str, str]` : Extrait diverses informations d'un fichier PDF.
    - `post(request, *args, **kwargs)` : Gère la requête POST pour ajouter un nouvel article.

    Exemple d'utilisation :
    ```python
    # Exemple d'utilisation de ArticleAdd
    class SomeView(APIView):
        def some_method(self, request):
            # Appel à ArticleAdd pour ajouter un nouvel article
            article_add_view = ArticleAdd()
            response = article_add_view.post(request)

    ```
    """
    def extractText(pdf_file : str) -> [str] :
        """
        Extrait le texte de toutes les pages d'un fichier PDF.

        Paramètres :
        - `pdf_file` : Chemin vers le fichier PDF.

        Retours :
        - Une liste de chaînes de texte extraites de chaque page du PDF.
        """
        with open(pdf_file , 'rb') as pdf:
            reader = PyPDF2.PdfFileReader(pdf ,strict=False)
            pdf_text = []
            for page in reader.pages:
                content = page.extract_text()
                pdf_text.append(content)
            return pdf_text
    def extract_authors(self,text):
       """
        Extrait les noms d'auteurs à partir du texte en utilisant spaCy.

        Paramètres :
        - `text` : Le texte à analyser.

        Retours :
        - Une liste de noms d'auteurs.
       """
       nlp = spacy.load("en_core_web_sm")
       doc = nlp(text)

       person_names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]

       return person_names

    def extract_organizations(self,text):
       """
        Extrait les organisations à partir du texte en utilisant spaCy.

        Paramètres :
        - `text` : Le texte à analyser.

        Retours :
        - Une liste d'organisations.
        """
       nlp = spacy.load("en_core_web_sm")
       doc = nlp(text)

       organizations = [ent.text for ent in doc.ents if ent.label_ == "ORG"]

       return organizations

    def extract(self,text:str,start_word:str,end_word:str):
       """
        Extrait le texte entre deux mots-clés spécifiés.

        Paramètres :
        - `text` : Le texte dans lequel effectuer l'extraction.
        - `start_word` : Le mot-clé de début.
        - `end_word` : Le mot-clé de fin.

        Retours :
        - Le texte extrait entre les mots-clés spécifiés.
        """
       parts = text.split("\n")
       collect = False
       result = ""
       for part in parts:
          comp_word = part.lower()
          if start_word in comp_word  :
             collect = True
             continue
          elif end_word in comp_word :
             collect=False
             break
          if collect == True:
            result += part+"\n"
       return result

    def extract_to(self,text:str,end_word:str):
        """
        Extrait le texte jusqu'à un mot-clé spécifié.

        Paramètres :
        - `text` : Le texte dans lequel effectuer l'extraction.
        - `end_word` : Le mot-clé de fin.

        Retours :
        - Le texte extrait jusqu'au mot-clé spécifié.
        """
        parts = text.split("\n")
        result = ""
        for part in parts:
            comp_word = part.lower()
            if comp_word.find(end_word) != -1:
                break
            result += part+"\n"
        return result

    def extract_organizations(self,text):
       
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)

        organizations = [ent.text for ent in doc.ents if ent.label_ == "ORG"]

        return organizations

    def extract_infos(self,pdf_name:str):
        
        doc = fitz.open(pdf_name)
        result = ""
        title = ""
        first_page = ""
        flag1 = True
        flag2 = True
        for page in doc:
            bboxes = column_boxes(page, footer_margin=50, no_image_text=True)
            for rect in bboxes:
                result += page.get_text(clip=rect, sort=True)
                if flag1:
                    title = result
                    flag1 = False
                if flag2 :
                    first_page += page.get_text(clip=rect, sort=True)
            flag2 = False

        resume = self.extract(result,"abstract","ccs")
        if (result.find("ACKNOWLEDGMENTS") != -1):
            content = self.extract(result ,"introduction" ,"acknowledgments")
        else:
            content = self.extract(result ,"introduction" ,"references")
        authors = ",".join(self.extract_authors(first_page))
        refrences = self.extract(result ,"references" , "fin_de_article")
        instit = ",".join(self.extract_organizations(self.extract_to(result,"ccs")))
        if "KEYWORDS" in result :
            keywords = self.extract(result ,"keywords" ,"acm")
        else:
            keywords = ""
        return title,authors,content,resume,refrences,instit,keywords

    def post(self ,request ,*args, **kwargs):
        """
        Gère la requête POST pour ajouter un nouvel article.

        Paramètres :
        - `request` : L'objet de requête HTTP Django.
        - `args` et `kwargs` : Arguments et mots-clés supplémentaires pouvant être passés à la vue.

        Retours :
        - Une réponse indiquant que l'article a été ajouté.
        """
        pdf = request.data["pdf"]
        temp = TempModel.objects.create(
            pdf = pdf
        )
        title,authors,content,resume,refrences,instit,keywords = self.extract_infos(temp.pdf.path)
        article = Article.objects.create(
            titre = title,
            auteurs = authors,
            contenu = content,
            resume = resume,
            references = refrences,
            pdf = pdf,
            institutions = instit,
            mot_cles = keywords
        )
         # Index the article in Elasticsearch
        connections.create_connection(hosts=['localhost:9200'])
        article_index = ArticleIndex(
            meta={'id': article.id},
            id=str(article.id),
            title=article.titre,
            sumup=article.resume,
            content=article.contenu,
            date=article.date_pub,
            keywords=article.mot_cles.split(',') if article.mot_cles else [],
            author=article.auteurs,
            institus=article.institutions.split(',') if article.institutions else [],
        )
        article_index.save()
        temp.delete()
        return Response("Article ajoutée")
    
class ArticleSearch(APIView):
    """
    Une vue basée sur les classes pour effectuer une recherche d'articles dans Elasticsearch.

    Cette vue prend en charge les requêtes GET pour rechercher des articles en fonction de différents critères tels que
    les mots-clés, les auteurs, les institutions et la plage de dates.

    Paramètres :
    - `request` : L'objet de requête HTTP Django.

    Retours :
    - Une réponse JSON contenant les résultats de la recherche d'articles.

    Méthodes :
    - `filter_by_keywords(search, keywords)` : Filtre la recherche par mots-clés.
    - `filter_by_authors(search, auteurs)` : Filtre la recherche par auteurs.
    - `filter_by_institutions(search, institutions)` : Filtre la recherche par institutions.
    - `filter_by_date_range(search, start_date, end_date)` : Filtre la recherche par plage de dates.
    - `get(request)` : Gère la requête GET pour effectuer la recherche d'articles.

    Exemple d'utilisation :
    ```python
    # Exemple d'utilisation de ArticleSearch
    class SomeView(APIView):
        def some_method(self, request):
            # Appel à ArticleSearch pour effectuer une recherche d'articles
            article_search_view = ArticleSearch()
            response = article_search_view.get(request)

    ```
    """
    def filter_by_keywords(self, search, keywords):
        """
        Filtre la recherche par mots-clés.

        Paramètres :
        - `search` : Objet de recherche Elasticsearch.
        - `keywords` : Mots-clés à utiliser dans la recherche.

        Retours :
        - L'objet de recherche Elasticsearch mis à jour avec le filtre des mots-clés.
        """
        return search.query('multi_match', query=keywords, fields=['title', 'resume', 'contenu', 'keywords'])
    
    def filter_by_authors(self, search, auteurs):
        """
        Filtre la recherche par auteurs.

        Paramètres :
        - `search` : Objet de recherche Elasticsearch.
        - `auteurs` : Auteurs à utiliser dans la recherche.

        Retours :
        - L'objet de recherche Elasticsearch mis à jour avec le filtre des auteurs.
        """
        return search.query(Q('terms', author=auteurs))

    def filter_by_institutions(self, search, institutions):
        """
        Filtre la recherche par institutions.

        Paramètres :
        - `search` : Objet de recherche Elasticsearch.
        - `institutions` : Institutions à utiliser dans la recherche.

        Retours :
        - L'objet de recherche Elasticsearch mis à jour avec le filtre des institutions.
        """
        return search.query(Q('terms', institus=institutions.split(',')))

    def filter_by_date_range(self, search, start_date, end_date):
        """
        Filtre la recherche par plage de dates.

        Paramètres :
        - `search` : Objet de recherche Elasticsearch.
        - `start_date` : Date de début de la plage.
        - `end_date` : Date de fin de la plage.

        Retours :
        - L'objet de recherche Elasticsearch mis à jour avec le filtre de la plage de dates.
        """
        return search.query(Range(date_pub={'gte': start_date, 'lte': end_date}))
    
    def get(self, request):
        # Get user's search query from the request
        """
        Gère la requête GET pour effectuer une recherche d'articles.

        Paramètres :
        - `request` : L'objet de requête HTTP Django.

        Retours :
        - Une réponse JSON contenant les résultats de la recherche d'articles.
        """
        search_query = request.GET.get('q', '')

        # Initialize pagination
        page = request.GET.get('page', 1)
        size = request.GET.get('size', 4)  # Number of results per page
        start = (int(page) - 1) * int(size)

        # Perform the Elasticsearch search with pagination
        search = Search(index='articles').query(
            'multi_match', query=search_query,
            fields=['titre', 'resume', 'contenu', 'keywords', 'author', 'institus']
        ).sort('-date_pub')[start:start + int(size)]

       # Apply filters
        keywords = request.GET.get('keywords')
        authors = request.GET.get('authors')
        institutions = request.GET.get('institutions')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if keywords:
            search = self.filter_by_keywords(search, keywords)

        if authors:
            search = self.filter_by_authors(search, authors)

        if institutions:
            search = self.filter_by_institutions(search, institutions)

        if start_date and end_date:
            search = self.filter_by_date_range(search, start_date, end_date)
        # Execute the search 
        response = search.execute()
        # Process and return search results
        results = []
        for hit in response:
            author_name = hit.author if hasattr(hit, 'author') else ''
            institus_names = hit.institus if hasattr(hit, 'institus') else []

            result_data = {
                'titre': hit.titre,
                'resume': hit.resume,
                'date_pub': hit.date_pub,
                'author': author_name,
                'institus': institus_names,
            }
            results.append(result_data)

        return Response({"results": results})

class ArticleFavoris(APIView):
    """
    Une vue basée sur les classes pour gérer les articles favoris d'un utilisateur.

    Cette vue prend en charge les requêtes POST et DELETE pour ajouter et supprimer des articles des favoris d'un utilisateur.

    Paramètres :
    - `request` : L'objet de requête HTTP Django.
    - `Userid` : L'identifiant de l'utilisateur.
    - `Artid` : L'identifiant de l'article.

    Retours :
    - Une réponse JSON indiquant la validation de l'opération.

    Méthodes :
    - `post(request, Userid, Artid)` : Gère la requête POST pour ajouter un article aux favoris d'un utilisateur.
    - `delete(request, Userid, Artid)` : Gère la requête DELETE pour supprimer un article des favoris d'un utilisateur.

    Exemple d'utilisation :
    ```python
    # Exemple d'utilisation de ArticleFavoris
    class SomeView(APIView):
        def some_method(self, request, Userid, Artid):
            # Ajout d'un article aux favoris
            article_favoris_view = ArticleFavoris()
            response_add = article_favoris_view.post(request, Userid, Artid)

            # Suppression d'un article des favoris
            response_delete = article_favoris_view.delete(request, Userid, Artid)

           
    ```
    """
    def post(self , request,Userid,Artid):
        """
        Gère la requête POST pour ajouter un article aux favoris d'un utilisateur.

        Paramètres :
        - `request` : L'objet de requête HTTP Django.
        - `Userid` : L'identifiant de l'utilisateur.
        - `Artid` : L'identifiant de l'article.

        Retours :
        - Une réponse JSON indiquant la validation de l'opération.
        """ 
        user = User.objects.get(id=Userid)
        user.favoris.add(Artid)
        return Response({
                "Validation" : "valid" , 
            })
    def delete(self , request,Userid,Artid): 
        """
        Gère la requête DELETE pour supprimer un article des favoris d'un utilisateur.

        Paramètres :
        - `request` : L'objet de requête HTTP Django.
        - `Userid` : L'identifiant de l'utilisateur.
        - `Artid` : L'identifiant de l'article.

        Retours :
        - Une réponse JSON indiquant le statut de la suppression de l'item.
        """
        try:
            obj=Article.objects.get(id=Userid)
        except Article.DoesNotExist:
            msg={"msg" : "Article not found"}
            return Response(msg,status=status.HTTP_404_NOT_FOUND)
        obj.favoris.remove(Artid)
        return Response({"status":"success","data":"item Deleted" })  
    

class ArticleGet(APIView):
    def get(self,request,pk):
        article = Article.objects.get(id=pk)
        serializer = ArticleSerializer(article,many=False)
        return Response(serializer.data)
    

    


class ArticleViewset(APIView):
    """
    Une vue basée sur les classes pour effectuer des opérations CRUD sur les articles.

    Cette vue prend en charge les requêtes POST, DELETE, PATCH et GET pour créer, supprimer, mettre à jour et récupérer des articles.

    Paramètres :
    - `request` : L'objet de requête HTTP Django.
    - `id` : L'identifiant de l'article.

    Retours :
    - Pour la requête POST :
        - Une réponse JSON indiquant le statut de l'opération et les données de l'article créé.
    - Pour la requête DELETE :
        - Une réponse JSON indiquant le statut de la suppression de l'article.
    - Pour la requête PATCH :
        - Une réponse JSON indiquant le statut de la mise à jour de l'article.
    - Pour la requête GET :
        - Une réponse JSON contenant la liste de tous les articles.

    Méthodes :
    - `post(request)` : Gère la requête POST pour créer un nouvel article.
    - `delete(request, id)` : Gère la requête DELETE pour supprimer un article.
    - `patch(request, id)` : Gère la requête PATCH pour mettre à jour un article.
    - `get(request)` : Gère la requête GET pour récupérer tous les articles.

    Exemple d'utilisation :
    ```python
    # Exemple d'utilisation de ArticleViewset
    class SomeView(APIView):
        def some_method(self, request):
            # Création d'un nouvel article
            article_viewset = ArticleViewset()
            response_post = article_viewset.post(request)

            # Suppression d'un article
            response_delete = article_viewset.delete(request, id=1)

            # Mise à jour d'un article
            response_patch = article_viewset.patch(request, id=1)

            # Récupération de tous les articles
            response_get = article_viewset.get(request)
         
    ```
    """
   
    # Post 
    def post (self,request):
        """
        Gère la requête POST pour créer un nouvel article.

        Paramètres :
        - `request` : L'objet de requête HTTP Django.

        Retours :
        - Une réponse JSON indiquant le statut de l'opération et les données de l'article créé.
        """
       
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status":"success","data":serializer.data},status=status.HTTP_200_OK)
        else:
            return Response({"status":"error","data":serializer.error},status=status.HTTP_400_BAD_REQUEST)
    #Delete 
    def delete(self,request,id):
        """
        Gère la requête DELETE pour supprimer un article.

        Paramètres :
        - `request` : L'objet de requête HTTP Django.
        - `id` : L'identifiant de l'article.

        Retours :
        - Une réponse JSON indiquant le statut de la suppression de l'article.
        """
        try:
            obj=Article.objects.get(id=id)
        except Article.DoesNotExist:
            msg={"msg" : "Article not found"}
            return Response(msg,status=status.HTTP_404_NOT_FOUND)
        obj.delete()  
        return Response({"status":"success","data":"item Deleted" })  
    
    #update  
    def patch(self, request, id):
        """
        Gère la requête PATCH pour mettre à jour un article.

        Paramètres :
        - `request` : L'objet de requête HTTP Django.
        - `id` : L'identifiant de l'article.

        Retours :
        - Une réponse JSON indiquant le statut de la mise à jour de l'article.
        """
        my_model = Article.objects.get(id=id)
        serializer = ArticleSerializer(my_model, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #Get all article 
    def get(self,request):
        """
        Gère la requête GET pour récupérer tous les articles.

        """
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles,many=True)


        return Response(serializer.data)
    




# c'est la fonction d'upload qui fait l'upload des fichiers pdf a partir d'in url de  google drive qui contient les pdf et puis les met dans le repertoire Uploaded files pour qu'on puisse les utiliser dans l'extraction apres envoyer le repertoire a la base des données de elastic search
# j'ai utiliser google drive API et Service account pour permettre a n'importe quel user d'uploader 
  
def download_from_drive_view(request,drive_url):
    """
    Une vue basée sur les fonctions pour télécharger des fichiers PDF à partir de Google Drive.

    Cette vue utilise PyDrive pour authentifier et interagir avec Google Drive, puis télécharge les fichiers PDF d'un dossier spécifié.

    Paramètres :
    - `request` : L'objet de requête HTTP Django.
    - `drive_url` : L'URL du dossier Google Drive à partir duquel télécharger les fichiers.

    Retours :
    - Une réponse HTTP indiquant le succès du téléchargement des fichiers PDF.

    Méthodes :
    - `download_from_drive_view(request, drive_url)` : Gère la requête pour télécharger des fichiers PDF depuis Google Drive.

    Exemple d'utilisation :
    ```python
    # Exemple d'utilisation de download_from_drive_view
    class SomeView(View):
        def some_method(self, request):
            # Appel à download_from_drive_view pour télécharger les fichiers PDF
            drive_url = 'https://drive.google.com/your_folder_url'
            download_from_drive_view(request, drive_url)

            # Traitement de la réponse
            # Votre code ici
    ```
    """

    gauth = GoogleAuth()
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'C:/Users/gigabyte/Desktop/TP_IGL/ProjetIGL-Backend/rechrchartc/rchrchArtcl/ServiceAccount.json',
        ['https://www.googleapis.com/auth/drive']
    )

    drive = GoogleDrive(gauth)

    download_directory = 'C:/Users/gigabyte/Desktop/TP_IGL/ProjetIGL-Backend/rechrchartc/UploadedFiles'

    # Extract folder ID from the Drive URL
    url_parts = drive_url.split('/')
    folder_id = url_parts[-1]  # Assuming the folder ID is at the end of the URL

    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()

    # Download only PDF files
    for index, file in enumerate(file_list):
        if file['title'].endswith('.pdf'):
            file_path = os.path.join(download_directory, file['title'])
            try:
                file.GetContentFile(file_path)
                print(f"{index+1}: File downloaded: {file['title']}")
            except:
                print(f"Failed to download: {file['title']}")

    return HttpResponse('PDF Files downloaded successfully!')
    
# c'est une fonction pour tester 
def Test(request):
    # Vous pouvez fournir ici le drive_url à la fonction download_from_drive_view
    drive_url = 'https://drive.google.com/drive/folders/1kadnheliuIjL6jDajVb06VoenM-E5p0c'
    response = download_from_drive_view(request, drive_url)
    return response


# c'est une fonction pour tester 
def Test(request):
    # Vous pouvez fournir ici le drive_url à la fonction download_from_drive_view
    drive_url = 'https://drive.google.com/drive/folders/1kadnheliuIjL6jDajVb06VoenM-E5p0c'
    response = download_from_drive_view(request, drive_url)
    return response


def check_elasticsearch_connection():
    try:
        # Initialize an Elasticsearch client
        es = Elasticsearch(['http://localhost:9200'])  # Replace with your Elasticsearch server details

        # Check the connection by pinging the Elasticsearch server
        if es.ping():
            return True  # Connection successful
        else:
            return False  # Ping failed
    except ConnectionError:
        return False 
    
def Test2(request):
    connected = check_elasticsearch_connection()
    if connected:
        return HttpResponse("Connected to Elasticsearch server.")
    else:
        return HttpResponse("Connection to Elasticsearch server failed.")
    

def get_article_details(request, article_id):
    """
    Une vue basée sur les fonctions pour récupérer les détails d'un article à partir d'Elasticsearch.

    Cette vue utilise l'ID de l'article pour interroger Elasticsearch et renvoie les détails de l'article en tant que réponse JSON.

    Paramètres :
    - `request` : L'objet de requête HTTP Django.
    - `article_id` : L'identifiant de l'article dans Elasticsearch.

    Retours :
    - Une réponse JSON contenant les détails de l'article ou une réponse JSON avec un message d'erreur si l'article n'est pas trouvé.

    Méthodes :
    - `get_article_details(request, article_id)` : Gère la requête pour récupérer les détails d'un article depuis Elasticsearch.

    Exemple d'utilisation :
    ```python
    # Exemple d'utilisation de get_article_details
    class SomeView(View):
        def some_method(self, request):
            # Appel à get_article_details pour récupérer les détails de l'article
            article_id = 'your_article_id'
            response = get_article_details(request, article_id)

         
    ```
    """
    es = Elasticsearch([f'http://elastic:8eCLcea63hBwu11_K9mu@localhost:9200'])

    try:
        # Retrieve the article from Elasticsearch using its ID
        article = es.get(index='index1', id=article_id) 

        # Return article details as JSON response
        return JsonResponse(article['_source'])
    except NotFoundError:
        return JsonResponse({'error': 'Article not found'}, status=404)

def delete_article(request, article_id):
    """
    Une vue basée sur les fonctions pour supprimer un article d'Elasticsearch.

    Cette vue utilise l'ID de l'article pour supprimer l'article de l'index Elasticsearch.

    Paramètres :
    - `request` : L'objet de requête HTTP Django.
    - `article_id` : L'identifiant de l'article dans Elasticsearch.

    Retours :
    - Une réponse JSON indiquant le succès de la suppression de l'article ou une réponse JSON avec un message d'erreur si l'article n'est pas trouvé.

    Méthodes :
    - `delete_article(request, article_id)` : Gère la requête pour supprimer un article depuis Elasticsearch.

    Exemple d'utilisation :
    ```python
    # Exemple d'utilisation de delete_article
    class SomeView(View):
        def some_method(self, request):
            # Appel à delete_article pour supprimer l'article
            article_id = 'your_article_id'
            response = delete_article(request, article_id)

          
    ```
    """
   
    # Initialize Elasticsearch client with authentication
    es = Elasticsearch([f'http://elastic:8eCLcea63hBwu11_K9mu@localhost:9200'])
    try:
        # Delete the article using its ID
        es.delete(index='index1', id=article_id)
        return JsonResponse({'message': 'Article deleted successfully'})
    except NotFoundError:
        return JsonResponse({'error': 'Article not found'}, status=404)        
 

  
    

def get_all_articles(request):
    """
    Une vue basée sur les fonctions pour récupérer tous les articles depuis Elasticsearch.

    Cette vue utilise une requête Elasticsearch pour rechercher tous les articles dans l'index spécifié et renvoie les données des articles en tant que réponse JSON.

    Paramètres :
    - `request` : L'objet de requête HTTP Django.

    Retours :
    - Une réponse JSON contenant tous les articles ou une réponse JSON avec un message d'erreur en cas d'échec.

    Méthodes :
    - `get_all_articles(request)` : Gère la requête pour récupérer tous les articles depuis Elasticsearch.

    Exemple d'utilisation :
    ```python
    # Exemple d'utilisation de get_all_articles
    class SomeView(View):
        def some_method(self, request):
            # Appel à get_all_articles pour récupérer tous les articles
            response = get_all_articles(request)

            # Traitement de la réponse
            # Votre code ici
    ```
    """
    try:     

        # Initialize Elasticsearch client with authentication
        es = Elasticsearch([f'http://elastic:8eCLcea63hBwu11_K9mu@localhost:9200'])

        # Search for all articles in the specified index
        search_results = es.search(index='index1', body={"query": {"match_all": {}}})

        # Extract article data from search results
        articles = [hit['_source'] for hit in search_results['hits']['hits']]

        # Return articles as standardized JSON response
        response_data = {
            'success': True,
            'message': 'Articles retrieved successfully',
            'data': {'articles': articles},
        }
        return JsonResponse(response_data)
    except Exception as e:
        # Return error as standardized JSON response
        error_response = {
            'success': False,
            'message': 'Error retrieving articles',
            'error': str(e),
        }
        return JsonResponse(error_response, status=500)    