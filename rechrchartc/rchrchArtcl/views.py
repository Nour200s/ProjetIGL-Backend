from django.shortcuts import render
from rest_framework.views import APIView 
from .api.serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed 
from .models import User 

class Registerview(APIView):
    def post(self , request): 
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer)
class Loginview(APIView):
    def post(self , request):
        name = request.data["name"]
        password = request.data["password"]
        user = User.objects.fielter(name=name).first()
        if user is None:
            raise AuthenticationFailed("User not found !")
        user = User.objects.fielter(password=password).first()
        if user is None :
           raise AuthenticationFailed("User not found !")
        return Response(
            {
                "message" : "match"
            }
        ) 