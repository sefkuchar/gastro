from rest_framework import permissions
from .models import Customer,Owner,Waiter


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class FullDjangoModelPermissions(permissions.DjangoModelPermissions):
    def __init__(self) -> None:
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class IsUserCustomer(permissions.BasePermission):
    def has_permission(self, request, view):        
         try:            
            customer = Customer.objects.get(user_id=request.user.id)
            return True
         except Customer.DoesNotExist:
            return bool(request.user and request.user.is_staff)

        
       
class IsUserOwner(permissions.BasePermission):
    def has_permission(self, request, view):       
         try:            
            owner = Owner.objects.get(user_id=request.user.id)
            return True
         except Owner.DoesNotExist:
            return bool(request.user and request.user.is_staff)

       

class IsUserWaiter(permissions.BasePermission):
    def has_permission(self, request, view):        
         try:            
            waiter = Waiter.objects.get(user_id=request.user.id)
            return True
         except Waiter.DoesNotExist:
            return bool(request.user and request.user.is_staff)

        
