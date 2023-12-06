from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
    
class Restaurant(models.Model):
    RestaurantTitle = models.CharField(max_length = 50)
    OwnerID  = models.ForeignKey("Person", on_delete=models.CASCADE,)
    EmployeeeIDS = ArrayField(models.IntegerField())
    TableGridID =  models.ForeignKey("TableGrid", on_delete=models.CASCADE,)
    Status = models.CharField(max_length=255)
    Location = models.CharField(max_length=255)
    def __str__(self):
        return self.RestaurantTitle
    

class TableGrid(models.Model):
    Rows = models.IntegerField(null = True)
    Columns = models.IntegerField(null = True)
    Tables = ArrayField(models.IntegerField())
    def __str__(self):
        return self.Rows, self.Columns



class Person(models.Model):
    
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

    role_choices  = (
        ('A', 'admin'),
        ('O','Owner'),
        ('W','Waiter'),
        ('C', 'Customer')
    )

    role = models.CharField(max_length=9,
                  choices=role_choices,
                  default="C")



    def __str__(self):
        return self.name
    
class Reservation(models.Model):
    
    Person = models.ForeignKey("Person", on_delete=models.CASCADE,)
    TableId = models.IntegerField(null = True)
    DateTimeFrom = models.DateTimeField()
    DateTimeTo = models.DateTimeField()
    PersonId = models.IntegerField(null = True)

    def __str__(self):
        return self.TableId
    
class Table(models.Model):
    status = models.CharField(max_length=255, null = True)
    seats = models.IntegerField(null = True)
    row = models.IntegerField(null = True)
    column = models.IntegerField(null = True)

    def __str__(self):
        return self.row, self.column


class Order(models.Model):
    Restaurant = models.ForeignKey("Restaurant", on_delete=models.CASCADE,)
    Table = models.ForeignKey("Table", on_delete=models.CASCADE,)
    Customer = models.ForeignKey("Person", on_delete=models.CASCADE,)
    Order = models.TextField()

    def __str__(self):
        return self.Order   