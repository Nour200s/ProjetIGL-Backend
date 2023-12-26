from django.urls import path 
from ..views import *

urlpatterns = [
    path('register',Registerview.as_view()) ,
    path('login',Loginview.as_view()),
    path('mods/',ModeratorList.as_view(),name="mods"),
    path('mods/new',ModeratorUpdate.as_view(),name="modcreate"),
    path('mods/<str:pk>',ModeratorUpdate.as_view(),name="modupdate"),
    path('mods/<str:pk>/delete',ModeratorUpdate.as_view(),name="moddelete")
]