from rest_framework.views import APIView 
from .api.serializers import *
from rest_framework.response import Response 
from dotenv import load_dotenv
from .models import *
from decouple import config
import jwt , datetime  
from oauth2client.service_account import ServiceAccountCredentials

from rest_framework import status
from .api import serializers

from . import models

import PyPDF2
from django.db import connections
from django.http import JsonResponse
from elasticsearch_dsl import Date, Document, Search, Text

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
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt

class Registerview(APIView):
    def post(self , request): 
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
    def post(self , request):
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
        payload = {
            "id" : user.id , 
            "exp" : datetime.datetime.utcnow() + datetime.timedelta(minutes=60*24*10) ,
            "iat" : datetime.datetime.utcnow()
        }
        token = jwt.encode(payload,'secret', algorithm="HS256")
        reponse = Response() 
        reponse.data = {
            "token" : token , 
             "visitor" : visitor 
        }
        reponse.set_cookie("SESSION",value=token) 
        return reponse 
    

class ModeratorList(APIView):
    def get(self,request):
        mods = Moderateurs.objects.all()
        serializer = ModerateursSerializer(mods,many=True)


        return Response(serializer.data)
    
class ModeratorUpdate(APIView):
    def get(self,request,pk):
        mods = Moderateurs.objects.get(id=pk)
        serializer = ModerateursSerializer(mods,many=False)
        return Response(serializer.data)
    def put(self,request,pk):
        data = request.data
        mod = Moderateurs.objects.get(id=pk)
        serializer = ModerateursSerializer(instance=mod ,data=data)

        if serializer.is_valid():
            serializer.save() 
        return Response(serializer.data)
    def delete(self,request,pk):
        mod = Moderateurs.objects.get(id=pk)
        mod.delete()
        return Response("Moderateur supprimé")
    def post(self,request):

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
    titre = Text(fields={'raw': Text(index=False)}) 
    resume = Text()
    contenu = Text()
    date_pub = Date()
    keywords = Text(multi=True)  
    author = Text()  
    institus = Text(multi=True)
    class Index:
        name = 'articles'
class ArticleAdd(APIView):
    def extractText(pdf_file : str) -> [str] :
        with open(pdf_file , 'rb') as pdf:
            reader = PyPDF2.PdfFileReader(pdf ,strict=False)
            pdf_text = []
            for page in reader.pages:
                content = page.extract_text()
                pdf_text.append(content)
            return pdf_text
    def extract_authors(self,text):
       nlp = spacy.load("en_core_web_sm")
       doc = nlp(text)

       person_names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]

       return person_names

    def extract_organizations(self,text):
       nlp = spacy.load("en_core_web_sm")
       doc = nlp(text)

       organizations = [ent.text for ent in doc.ents if ent.label_ == "ORG"]

       return organizations

    def extract(self,text:str,start_word:str,end_word:str):
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
        pdf = request.data["pdf"]
        temp = TempModel.objects.create(
            pdf = pdf
        )
        title,authors,content,resume,refrences,instit,keywords = self.extract_infos(temp.pdf.path)
        Article.objects.create(
            titre = title,
            auteurs = authors,
            contenu = content,
            resume = resume,
            references = refrences,
            pdf = pdf,
            institutions = instit,
            mot_cles = keywords
        )
        temp.delete()
        


        return Response("Article ajoutée")
class ArticleViewset(APIView):
    def get(self,request,id=None):
        if id:
            item = models.Article.objects.get(id=id)
            serializer = serializers.ArticleSerializer(item)
            return Response({"status":"success","data":serializer.data},status=status.HTTP_200_OK)
        items=models.Article.objects.all()
        serializer = serializers.ArticleSerializer(items,many=True)
        return Response({"status":"success","data":serializer.data},status=status.HTTP_200_OK)
    

    # Post 
    def post (self,request):
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status":"success","data":serializer.data},status=status.HTTP_200_OK)
        else:
            return Response({"status":"error","data":serializer.error},status=status.HTTP_400_BAD_REQUEST)
        
    # Patch
   

    def patch(self, request, id=None):
        try:
            article_instance = models.Article.objects.get(id=id)
        except models.Article.DoesNotExist:
            return Response({"status": "error", "message": "Article not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.ArticleSerializer(article_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"status": "error", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    #Delete 
    def delete(self,request,id):
        try:
            obj=Article.objects.get(id=id)
        except Article.DoesNotExist:
            msg={"msg" : "Article not found"}
            return Response(msg,status=status.HTTP_404_NOT_FOUND)
        obj.delete()  
        return Response({"status":"success","data":"item Deleted" })           
    

    def patch_references(self, request, id=None):
        try:
            article_instance = models.Article.objects.get(id=id)
        except models.Article.DoesNotExist:
            return Response({"status": "error", "message": "Article not found."}, status=status.HTTP_404_NOT_FOUND)

        references_data = request.data.get('references', {})  # Assuming references are in the request payload

        serializer = serializers.ReferencesSerializer(
            instance=article_instance.references,
            data=references_data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"status": "error", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # Associate the Article with author, institutions, and keywords
        article.authors.add(author)
        article.institus.set(institus)
        article.keywords.set(keywords_objs)

        # Index the article in Elasticsearch
        connections.create_connection(hosts=['localhost:9200'])
        article_index = ArticleIndex(
            titre=article.titre,
            resume=article.resume,
            contenu=article.contenu,
            date_pub=article.date_pub,
            keywords=[keyword.mot for keyword in keywords_objs],
            author=article.authors.first().nom if article.authors.exists() else '',
            institus=[institus.nom for institus in article.institus.all()]
        )
        article_index.save()

        return JsonResponse({'message': 'Article indexed successfully'})
    



class ArticleSearch(APIView):
    def get(self, request):
        # Get user's search query from the request
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
    def post(self , request,Userid,Artid): 
        user = User.objects.get(id=Userid)
        user.favoris.add(Artid)
        return Response({
                "Validation" : "valid" , 
            })
    def delete(self , request,Userid,Artid): 
        try:
            obj=Article.objects.get(id=Userid)
        except Article.DoesNotExist:
            msg={"msg" : "Article not found"}
            return Response(msg,status=status.HTTP_404_NOT_FOUND)
        obj.favoris.remove(Artid)
        return Response({"status":"success","data":"item Deleted" })  
class ArticleViewset(APIView):
    # Post 
    def post (self,request):
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status":"success","data":serializer.data},status=status.HTTP_200_OK)
        else:
            return Response({"status":"error","data":serializer.error},status=status.HTTP_400_BAD_REQUEST)
    #Delete 
    def delete(self,request,id):
        try:
            obj=Article.objects.get(id=id)
        except Article.DoesNotExist:
            msg={"msg" : "Article not found"}
            return Response(msg,status=status.HTTP_404_NOT_FOUND)
        obj.delete()  
        return Response({"status":"success","data":"item Deleted" })  
    #update  
    def patch(self, request, id):
        my_model = Article.objects.get(id=id)
        serializer = ArticleSerializer(my_model, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #Get all article 
    def get(self,request):
        articales =   Article.objects.all() 
        return Response(articales)
# c'est la fonction d'upload qui fait l'upload des fichiers pdf a partir d'in url de  google drive qui contient les pdf et puis les met dans le repertoire Uploaded files pour qu'on puisse les utiliser dans l'extraction apres envoyer le repertoire a la base des données de elastic search
# j'ai utiliser google drive API et Service account pour permettre a n'importe quel user d'uploader 
  
def download_from_drive_view(request,drive_url):
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
    es = Elasticsearch([f'http://elastic:8eCLcea63hBwu11_K9mu@localhost:9200'])

    try:
        # Retrieve the article from Elasticsearch using its ID
        article = es.get(index='index1', id=article_id) 

        # Return article details as JSON response
        return JsonResponse(article['_source'])
    except NotFoundError:
        return JsonResponse({'error': 'Article not found'}, status=404)

def delete_article(request, article_id):
   
    # Initialize Elasticsearch client with authentication
    es = Elasticsearch([f'http://elastic:8eCLcea63hBwu11_K9mu@localhost:9200'])
    try:
        # Delete the article using its ID
        es.delete(index='index1', id=article_id)
        return JsonResponse({'message': 'Article deleted successfully'})
    except NotFoundError:
        return JsonResponse({'error': 'Article not found'}, status=404)        
 

  
    

def get_all_articles(request):
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