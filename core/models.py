from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    birth_date = models.DateField(null=True)
    