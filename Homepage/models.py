from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    User_ID= models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    Auth_Image =models.CharField(max_length=15)
    key =models.CharField(max_length=100)