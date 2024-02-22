from django.contrib import admin
from . import models
from django.db.models import Count
from django.urls import reverse
from django.utils.html import urlencode
from django.utils.html import format_html
# Register your models here.

################################################################################## |
#Túto časť robil Matej Turňa                                                       |  
################################################################################## V

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name','orders']    
    list_per_page = 10
    list_select_related = ['user']
    ordering = ['user__first_name','user__last_name']
    search_fields =['user__first_name__istartswith','user__last_name__istartswith']


    @admin.display(ordering='orders') ######
    def orders(self,customer):
        url = (
            (reverse('admin:gastro_order_changelist')
            +"?"
            +urlencode({
            'customer__id': str(customer.id)
        }))
        )
        return  format_html('<a href="{}">{}</a>',url,customer.orders)  
    def get_queryset(self,request):
        return super().get_queryset(request).annotate(
            orders = Count('order')
        )
    
@admin.register(models.Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name','restaurant_title']    
    list_per_page = 10
    list_select_related = ['user','restaurant']
    ordering = ['user__first_name','user__last_name']
    search_fields =['first_name__istartswith','last_name__istartswith']

    def restaurant_title(self,Owner):
        return Owner.restaurant.restaurant_title


    

@admin.register(models.Waiter)
class WaiterAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name','restaurant_title']    
    list_per_page = 10
    list_select_related = ['user','restaurant']
    ordering = ['user__first_name','user__last_name']
    search_fields =['first_name__istartswith','last_name__istartswith']

    
    def restaurant_title(self,Owner):
        return Owner.restaurant.restaurant_title

@admin.register(models.Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['restaurant_status', 'restaurant_title']    
    list_per_page = 10    
    ordering = ['restaurant_title','restaurant_status']
    search_fields =['restaurant_title','restaurant_status']

@admin.register(models.RestaurantTable)
class TableAdmin(admin.ModelAdmin):
    autocomplete_fields = ['restaurant']
    search_fields = ['id']
    list_select_related = ['restaurant']
    list_display = ['id','restaurant','seats','table_status']

@admin.register(models.TableReservation)
class ReservationAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer','table']
    list_display = ['customer','date_time_from','table']
    search_fields = ['table__id']
    
##################################################################################
##################################################################################
##################################################################################

################################################################################## |
#Túto časť robil Adam Turčan                                                       |  
################################################################################## V
@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    search_fields=['title']
    list_display = ['title','products_count']
    @admin.display(ordering='products_count')
    def products_count(self,collection):
        url = (reverse('admin:gastro_product_changelist') 
        + '?'
        + urlencode({
            'collection_id': str(collection.id)
        }))
        
        return  format_html('<a href="{}">{}</a>',url,collection.products_count)  
    

    def get_queryset(self,request):
        return super().get_queryset(request).annotate(
            products_count = Count('products')
        )


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    
    autocomplete_fields = ['collection']
    search_fields = ['title']
    prepopulated_fields = {
        'slug':['title']
    }      
    list_display = ['title','unit_price', 'collection_title']
    list_editable = ['unit_price']
    list_per_page = 10
    list_select_related = ['collection']
    list_filter = ['collection','last_update']
    def collection_title(self,product):
        return product.collection.title 


class OrderItemInline(admin.StackedInline):
    autocomplete_fields = ['product']
    model = models.OrderItem
    extra = 0
    max_num = 10
    min_num = 1


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer','restaurant'  ]
    list_select_related =['restaurant','customer']
    inlines  = [OrderItemInline]
    list_filter = ['customer']
    list_display = ['id', 'placed_at', 'customer']  
##################################################################################
##################################################################################
##################################################################################
