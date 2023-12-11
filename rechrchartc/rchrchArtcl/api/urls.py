from django.urls import path 
from ..views import Registerview , Loginview

urlpatterns = [
    path('register',Registerview.as_view()) ,
    path('login',Loginview.as_view())
]