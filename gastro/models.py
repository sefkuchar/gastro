from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator
from django.conf import settings
from uuid import uuid4
from django.contrib import admin


class Restaurant(models.Model):
    RESTAURANT_OPEN = 'O'
    RESTAURARNT_CLOSED = 'C'

    RESTAURANT_STATUSES=[
        (RESTAURANT_OPEN,'Open'),
        (RESTAURARNT_CLOSED,"Closed")
    ]
    table_grid_width = models.IntegerField()
    table_grid_height = models.IntegerField()
    restaurant_title = models.CharField(max_length = 255)            
    restaurant_status = models.CharField(max_length=1,choices=RESTAURANT_STATUSES,default=RESTAURARNT_CLOSED)    
    

    def __str__(self)->str:
        return self.restaurant_title





class RestaurantTable(models.Model):
    restaurant = models.ForeignKey(Restaurant,on_delete=models.CASCADE,related_name="tables")

    seats = models.IntegerField(null = True)
    row = models.IntegerField(null = True)
    column = models.IntegerField(null = True)


    TABLE_EMPTY = 'E'    
    TABLE_FULL = 'F'    

    TABLE_STATUSES = [
        (TABLE_EMPTY,"Empty"),
        (TABLE_FULL,"Full"),        
    ]

    table_status = models.CharField(max_length=1,choices=TABLE_STATUSES, default=TABLE_EMPTY)



class Customer(models.Model):
    phone = models.CharField(max_length=255)            
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name
    @admin.display(ordering='user__last_name')   
    def last_name(self):
        return self.user.last_name

    def __str__(self) -> str:
      return f'{self.user.first_name} {self.user.last_name }'

    class Meta:
        ordering = ['user__first_name','user__last_name']



class Owner(models.Model):
    restaurant = models.OneToOneField(Restaurant,on_delete=models.CASCADE)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name
    @admin.display(ordering='user__last_name')   
    def last_name(self):
        return self.user.last_name

    def __str__(self) -> str:
      return f'{self.user.first_name} {self.user.last_name }'

    class Meta:
        ordering = ['user__first_name','user__last_name']


class Waiter(models.Model):
    restaurant = models.ForeignKey(Restaurant,on_delete=models.CASCADE,related_name='waiters')        
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name
    @admin.display(ordering='user__last_name')   
    def last_name(self):
        return self.user.last_name

    def __str__(self) -> str:
      return f'{self.user.first_name} {self.user.last_name }'

    class Meta:
        ordering = ['user__first_name','user__last_name']

class TableReservation(models.Model):    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    table = models.ForeignKey(RestaurantTable,on_delete=models.CASCADE,related_name='reservations')
    date_time_from = models.DateTimeField()
    date_time_to = models.DateTimeField()
        

class Collection(models.Model):
    title = models.CharField(max_length=255)
    restaurant = models.ForeignKey(Restaurant,on_delete=models.CASCADE,related_name='collections')
    featured_product = models.ForeignKey('Product',on_delete=models.SET_NULL,null=True,blank=True,related_name="+")
    def __str__(self) -> str :
        return self.title
    class Meta:
        ordering = ['title']    

class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()    
    description = models.TextField(null=True,blank=True)
    unit_price = models.DecimalField(max_digits=6,decimal_places=2, validators=[MinValueValidator(1)])    
    collection = models.ForeignKey(Collection,on_delete=models.PROTECT, related_name='products')
    restaurant = models.ForeignKey(Restaurant,on_delete=models.CASCADE,related_name='products')
    
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title
    class Meta:
        ordering = ['title']   

class Order(models.Model):
    ORDER_PENDING = 'P'
    ORDER_COMPLETE = 'C'
    ORDER_FAILED = 'F'    

    ORDER_STATUSES = [
        (ORDER_PENDING,"Pending"),
        (ORDER_COMPLETE,"Complete"),
        (ORDER_FAILED,"Failed")
    ]

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE,)
    table = models.ForeignKey(RestaurantTable, on_delete=models.CASCADE,)
    order = models.TextField()

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=1,choices=ORDER_STATUSES,default=ORDER_PENDING)
    customer = models.ForeignKey(Customer,on_delete=models.PROTECT)    


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=  models.PROTECT,related_name='items')
    product = models.ForeignKey(Product,on_delete = models.PROTECT,related_name='orderitems')
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6,decimal_places=2)

    class Meta:
        unique_together = [['order','product']]

class Cart(models.Model):
    id= models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete= models.CASCADE, related_name='items')
    product  = models.ForeignKey(Product, on_delete=models.CASCADE) 
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        unique_together = [['cart','product']]


#####
class Review(models.Model):
    product  = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='reviews')
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)

