from django.urls import path 
from rest_framework.routers import DefaultRouter
from .views import UserviewSet

post_router = DefaultRouter()
post_router.register(r'rchrchArtcl', UserviewSet)