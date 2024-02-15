from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

# Create your models here.

################################################################################## |
#Túto časť robil Matej Turňa                                                       |  
################################################################################## V

class User(AbstractUser):
    email = models.EmailField(unique=True)
    birth_date = models.DateField(null=True)
    