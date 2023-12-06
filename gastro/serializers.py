from rest_framework import serializers
from .models import Person, Restaurant, TableGrid, Reservation, Table, Order

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ('id', 'name', 'email',"password", "role")

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ('RestaurantTitle', 'OwnerID', 'EmployeeeIDS',"TableGridID", 'Status', 'Location')

class TableGridSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableGrid
        fields = ('Rows', 'Columns', 'Tables')

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ('Person', 'TableId', 'DateTimeFrom', 'DateTimeTo', 'PersonId')

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ('status', 'seats', 'row', 'column')

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('Restaurant', 'Table', 'Customer', 'Order')