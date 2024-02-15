from rest_framework import generics,status,filters
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,UpdateModelMixin
from rest_framework.viewsets import ModelViewSet,GenericViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, DjangoModelPermissions, DjangoModelPermissionsOrAnonReadOnly, IsAdminUser, IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes

from .filters import ProductFilter
from .pagination import DefaultPagination
from .permissions import FullDjangoModelPermissions, IsAdminOrReadOnly,IsUserCustomer,IsUserOwner,IsUserWaiter
from .models import  Cart, CartItem,Customer,Product,Collection,Waiter,RestaurantTable,TableReservation,Owner,Restaurant,Order,OrderItem
from .serializers import CartSerializer,CartItemSerializer,AddCartItemSerializer, UpdateCartItemSerializer,CustomerSerializer,ProductSerializer , \
CollectionSerializer,CreateOrderSerializer,WaiterSerializer,RestaurantTableSerializer,TableReservationSerializer,RestaurantSerializer,OrderSerializer,UpdateOrderSerializer

from django_filters.rest_framework import DjangoFilterBackend
from django.db.models.aggregates import Count


################################################################################## |
#Túto cast robil Adam Turčan                                                       |  
################################################################################## V

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination    
    search_fields = ['title', 'description','restaurant']
    ordering_fields = ['unit_price', 'last_update']
    permission_classes = [IsAuthenticated] 


    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({"error": "Product does not exist."}, status=status.HTTP_404_NOT_FOUND)

    def get_queryset(self):
        search_query = self.request.query_params.get('restaurant', None)
        try:
            owner = Owner.objects.get(user=self.request.user)
            restaurant = owner.restaurant
            if search_query:
                queryset = Product.objects.filter(restaurant_id=search_query)
            else:
                queryset = Product.objects.filter(restaurant=restaurant)
        except Owner.DoesNotExist:
            try:
                waiter = Waiter.objects.get(user=self.request.user)
                restaurant = waiter.restaurant

                if search_query:
                    queryset = Product.objects.filter(restaurant_id=search_query)
                else:     
                    queryset = Product.objects.filter(restaurant=restaurant)
            except Waiter.DoesNotExist:                      
                if search_query:
                    queryset = Product.objects.filter(restaurant_id=search_query)
                    
                else:
                    queryset = Product.objects.none()
                              
        return queryset

    def create(self,request,*args,**kwargs):
        try:
                user = request.user
                restaurant = None
            
                owner = Owner.objects.filter(user=user).first()
                if owner:
                    restaurant = owner.restaurant
                else:
            
                    waiter = Waiter.objects.filter(user=user).first()
                    if waiter:
                        restaurant = waiter.restaurant
                
                if restaurant:
                    serializer = self.get_serializer(data=request.data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(restaurant=restaurant) 
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": "You are not associated with any restaurant. Unable to create product."}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            product = self.get_object()
            user = request.user
                        
            owner = Owner.objects.filter(user=user, restaurant=product.restaurant).first()
            waiter = Waiter.objects.filter(user=user, restaurant=product.restaurant).first()
                        
            if owner or waiter:
                if OrderItem.objects.filter(product=product).exists():
                    return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
                self.perform_destroy(product)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "You are not authorized to delete this product."}, status=status.HTTP_403_FORBIDDEN)
        except :
            return Response({'error': 'Product does not exist.'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            user = request.user
                        
            owner = Owner.objects.filter(user=user, restaurant=instance.restaurant).first()
            waiter = Waiter.objects.filter(user=user, restaurant=instance.restaurant).first()
                        
            if owner or waiter:
                serializer = self.get_serializer(instance, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
            else:
                return Response({"error": "You are not authorized to update this product."}, status=status.HTTP_403_FORBIDDEN)
            
        except Product.DoesNotExist:
            return Response({"error": "Product does not exist."}, status=status.HTTP_404_NOT_FOUND)
   
class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(
        products_count=Count('products')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAuthenticated] 

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Collection.DoesNotExist:
            return Response({"error": "Collection does not exist."}, status=status.HTTP_404_NOT_FOUND)

    def get_queryset(self):
        search_query = self.request.query_params.get('restaurant', None)
        try:
            owner = Owner.objects.get(user=self.request.user)
            restaurant = owner.restaurant
            if search_query:
                queryset = Collection.objects.filter(restaurant_id=search_query)
            else:
                queryset = Collection.objects.filter(restaurant=restaurant)
        except Owner.DoesNotExist:
            try:
                waiter = Waiter.objects.get(user=self.request.user)
                restaurant = waiter.restaurant

                if search_query:
                    queryset = Collection.objects.filter(restaurant_id=search_query)
                else:     
                    queryset = Collection.objects.filter(restaurant=restaurant)
            except Waiter.DoesNotExist:                      
                if search_query:
                    queryset = Collection.objects.filter(restaurant_id=search_query)
                    
                else:
                    queryset = Collection.objects.none()
                              
        return queryset

    def create(self,request,*args,**kwargs):
        try:
                user = request.user
                restaurant = None
            
                owner = Owner.objects.filter(user=user).first()
                if owner:
                    restaurant = owner.restaurant
                else:
            
                    waiter = Waiter.objects.filter(user=user).first()
                    if waiter:
                        restaurant = waiter.restaurant
            
                if restaurant:
                    serializer = self.get_serializer(data=request.data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(restaurant=restaurant) 
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": "You are not associated with any restaurant. Unable to create collection."}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            collection = self.get_object()
            user = request.user
                    
            owner = Owner.objects.filter(user=user, restaurant=collection.restaurant).first()
            waiter = Waiter.objects.filter(user=user, restaurant=collection.restaurant).first()
                    
            if owner or waiter:
                if Product.objects.filter(collection_id=kwargs['pk']).exists():
                     return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
                self.perform_destroy(collection)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "You are not authorized to delete this collection."}, status=status.HTTP_403_FORBIDDEN)
        except :
            return Response({'error': 'Collection does not exist.'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            user = request.user
                        
            owner = Owner.objects.filter(user=user, restaurant=instance.restaurant).first()
            waiter = Waiter.objects.filter(user=user, restaurant=instance.restaurant).first()
                        
            if owner or waiter:
                serializer = self.get_serializer(instance, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
            else:
                return Response({"error": "You are not authorized to update this collection."}, status=status.HTTP_403_FORBIDDEN)
            
        except Product.DoesNotExist:
            return Response({"error": "Collection does not exist."}, status=status.HTTP_404_NOT_FOUND)

class CartViewSet(CreateModelMixin,
                  RetrieveModelMixin,
                  GenericViewSet,
                  DestroyModelMixin):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer
    permission_classes = [IsUserCustomer]
    
class CartItemViewSet(ModelViewSet):
    http_method_names = ['get','post','patch','delete']
    permission_classes = [IsUserCustomer]

    def get_serializer_class(self):
        if self.request.method   == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer        
        return CartItemSerializer    

    def get_serializer_context(self):
        return {'cart_id':self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')

class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):        
        return [IsUserCustomer()]
    
    def create(self, request, *args, **kwargs):
        
        restaurant_id = request.data.get('restaurant_id')
        table_id = request.data.get('table_id')
        if not restaurant_id:
            return Response({"error": "restaurant_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not table_id:
            return Response({"error": "table_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            restaurant = Restaurant.objects.get(pk=restaurant_id)
            table = RestaurantTable.objects.get(pk=table_id)
        except (Restaurant.DoesNotExist, RestaurantTable.DoesNotExist):
            return Response({"error": "Restaurant or Table with the provided ID does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CreateOrderSerializer(
            data=request.data,
            context={'user_id': request.user.id, 'restaurant': restaurant, 'table': table})
        serializer.is_valid(raise_exception=True)

        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer
        
    @action(detail=False, methods=['GET'], url_path='me')
    def me(self, request):
        user = request.user
        try:
            customer = Customer.objects.get(user=user)
            reservations = Order.objects.filter(customer=customer)
            serializer = self.get_serializer(reservations, many=True)
            return Response(serializer.data)
        except Customer.DoesNotExist:
            return Response({"error": "No Customer object associated with the request user."}, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
         return Response({"error": "Orders are not allowed to be deleted for safety purposes."}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
                        
            user = request.user
            restaurant = instance.restaurant
            
            if Owner.objects.filter(user=user, restaurant=restaurant).exists() or Waiter.objects.filter(user=user, restaurant=restaurant).exists():
                serializer = self.get_serializer(instance, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
            else:
                return Response({"error": "You are not authorized to update this Order."}, status=status.HTTP_403_FORBIDDEN)
            
        except RestaurantTable.DoesNotExist:
            return Response({"error": "Order does not exist."}, status=status.HTTP_404_NOT_FOUND)

    def get_queryset(self):
        user = self.request.user
        try:
            owner = Owner.objects.get(user=user)            
            restaurant = owner.restaurant
            queryset = Order.objects.filter(table__restaurant=restaurant)
        except Owner.DoesNotExist:
            try:
                waiter = Waiter.objects.get(user=user)                
                restaurant = waiter.restaurant
                queryset = Order.objects.filter(table__restaurant=restaurant)
            except Waiter.DoesNotExist: 
                customer = Customer.objects.get(user=user)
                queryset = Order.objects.filter(customer=customer)
                    
        return queryset 
##################################################################################
##################################################################################
##################################################################################




################################################################################## |
#Túto časť robil Matej Turňa                                                       |  
################################################################################## V
class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer    
    permission_classes = [IsAdminUser]
  
    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer = Customer.objects.get(user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        elif self.action == 'me':
            return [IsAuthenticated()]
        else:
            return super().get_permissions()

class WaiterViewSet(ModelViewSet):
    queryset = Waiter.objects.all()
    serializer_class = WaiterSerializer    
    permission_classes = [IsUserOwner]
  
    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer = Customer.objects.get(user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def get_queryset(self):
        
        owner = Owner.objects.get(user=self.request.user)
        
        restaurant = owner.restaurant
        
        queryset = Waiter.objects.filter(restaurant=restaurant)
        return queryset

    def get_permissions(self):    
        if self.action == 'me':
            return [IsUserWaiter()]
        else:
            return super().get_permissions()

class RestaurantTableView(ModelViewSet):
    queryset = RestaurantTable.objects.all()
    serializer_class = RestaurantTableSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['restaurant__id']

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except RestaurantTable.DoesNotExist:
            return Response({"error": "Restaurant table does not exist."}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            user = request.user
            restaurant = instance.restaurant
            
            if Owner.objects.filter(user=user, restaurant=restaurant).exists() or \
               Waiter.objects.filter(user=user, restaurant=restaurant).exists():
                self.perform_destroy(instance)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "You are not authorized to delete this item."}, status=status.HTTP_403_FORBIDDEN)
            
        except RestaurantTable.DoesNotExist:
            return Response({"error": "Restaurant table does not exist."}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
                        
            user = request.user
            restaurant = instance.restaurant
            
            if Owner.objects.filter(user=user, restaurant=restaurant).exists() or Waiter.objects.filter(user=user, restaurant=restaurant).exists():
                serializer = self.get_serializer(instance, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
            else:
                return Response({"error": "You are not authorized to update this restaurant table."}, status=status.HTTP_403_FORBIDDEN)
            
        except RestaurantTable.DoesNotExist:
            return Response({"error": "Restaurant table does not exist."}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            restaurant = None
            
            owner = Owner.objects.filter(user=user).first()
            if owner:
                restaurant = owner.restaurant
            else:
            
                waiter = Waiter.objects.filter(user=user).first()
                if waiter:
                    restaurant = waiter.restaurant
            
            if restaurant:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(restaurant=restaurant) 
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "You are not associated with any restaurant. Unable to create table."}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        search_query = self.request.query_params.get('restaurant', None)
        try:
            owner = Owner.objects.get(user=self.request.user)
            restaurant = owner.restaurant
            if search_query:
                queryset = RestaurantTable.objects.filter(restaurant_id=search_query)
            else:
                queryset = RestaurantTable.objects.filter(restaurant=restaurant)
        except Owner.DoesNotExist:
            try:
                waiter = Waiter.objects.get(user=self.request.user)
                restaurant = waiter.restaurant

                if search_query:
                    queryset = RestaurantTable.objects.filter(restaurant_id=search_query)
                else:     
                    queryset = RestaurantTable.objects.filter(restaurant=restaurant)
            except Waiter.DoesNotExist:                      
                if search_query:
                    queryset = RestaurantTable.objects.filter(restaurant_id=search_query)
                    
                else:
                    queryset = RestaurantTable.objects.none()
                              
        return queryset

class TableReservationView(ModelViewSet):
    queryset = TableReservation.objects.all()
    serializer_class = TableReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        
        owner_reservations = TableReservation.objects.none()
        waiter_reservations = TableReservation.objects.none()
        customer_reservations = TableReservation.objects.none()

        try:
            owner = Owner.objects.get(user=user)            
            restaurant = owner.restaurant
            owner_reservations = TableReservation.objects.filter(table__restaurant=restaurant)
        except Owner.DoesNotExist:
            pass
            
        try:
            waiter = Waiter.objects.get(user=user)                
            restaurant = waiter.restaurant
            waiter_reservations = TableReservation.objects.filter(table__restaurant=restaurant)
        except Waiter.DoesNotExist: 
            pass

        try:
            customer = Customer.objects.get(user=user)
            customer_reservations = TableReservation.objects.filter(customer=customer)
        except Customer.DoesNotExist:
            pass

    
        queryset = owner_reservations | waiter_reservations | customer_reservations
        return queryset.distinct()

    @action(detail=False, methods=['GET'], url_path='me')
    def me(self, request):
        user = request.user
        try:
            customer = Customer.objects.get(user=user)
            reservations = TableReservation.objects.filter(customer=customer)
            serializer = self.get_serializer(reservations, many=True)
            return Response(serializer.data)
        except Customer.DoesNotExist:
            return Response({"error": "No Customer object associated with the request user."}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        reservation = self.get_object()
        user = request.user
        restaurant = reservation.table.restaurant if reservation.table else None

        if reservation.customer.user == user:
            return super().update(request, *args, **kwargs)

        if restaurant:
            if Owner.objects.filter(user=user, restaurant=restaurant).exists() or Waiter.objects.filter(user=user, restaurant=restaurant).exists():
                return super().update(request, *args, **kwargs)
            else:
                return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"error": "No restaurant associated with the reservation's table."}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        reservation = self.get_object()
        user = request.user
        restaurant = reservation.table.restaurant if reservation.table else None

        if reservation.customer.user == user:
            return super().destroy(request, *args, **kwargs)

        if restaurant:
            if Owner.objects.filter(user=user, restaurant=restaurant).exists() or Waiter.objects.filter(user=user, restaurant=restaurant).exists():
                return super().destroy(request, *args, **kwargs)
            else:
                return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"error": "No restaurant associated with the reservation's table."}, status=status.HTTP_400_BAD_REQUEST)
    def perform_create(self, serializer):
        customer = Customer.objects.get(user=self.request.user)
        serializer.save(customer=customer)

class RestaurantViewSet(ReadOnlyModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [AllowAny]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if not request.user.is_authenticated:
            return Response({"error": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        
        user = request.user
        owner_exists = Owner.objects.filter(user=user).exists()
        waiter_exists = Waiter.objects.filter(user=user).exists()

        if owner_exists or waiter_exists:
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({"error": "You are not authorized to update this restaurant."}, status=status.HTTP_403_FORBIDDEN)
##################################################################################
##################################################################################    
##################################################################################


