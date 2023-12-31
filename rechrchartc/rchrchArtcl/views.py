from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView 
from .api.serializers import UserSerializer ,ModerateursSerializer,InstitutionSerializer,AuteursSerializer,MotCleSerializer,ReferencesSerializer,ArticleSerializer
from rest_framework.response import Response 

from .models import User ,Moderateurs, Admins,Institution,Article,Mot_cle,References,Auteurs

import jwt , datetime  
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.urls import reverse_lazy

from rest_framework import status
from .api import serializers
import PyPDF2
from . import models

import PyPDF2
from django.db import connections
from django.http import JsonResponse
from elasticsearch_dsl import Date, Document, Search, Text
from rest_framework.pagination import PageNumberPagination


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


    def post(self,request):
        pdf = request.data[""]
    
        # Retrieve Article instance and related objects
        article = Article.objects.create(
            titre=titre,
            resume=resume,
            contenu=contenu,
            date_pub=date_pub
        )
        author = Auteurs.objects.get(id=author_id)
        institus = Institution.objects.filter(id__in=institus_ids)
        keywords_objs = Mot_cle.objects.filter(mot__in=keywords)

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

