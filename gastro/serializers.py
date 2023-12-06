from rest_framework import serializers
from .models import Person, Restaurant
class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ('id', 'name', 'email',"password", "role")

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ('RestaurantTitle', 'OwnerID', 'EmployeeeIDS',"TableGridID", 'Status', 'Location')