from django.urls import path 
from . import views

app_name='homepage'

urlpatterns = [
    path('', views.index , name="index" ),
    path('facecheck/', views.FaceCheck , name="faceCheck"),
    path('drive/', views.drive, name="Drive"),
]
