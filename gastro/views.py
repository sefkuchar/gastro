from rest_framework import generics
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,UpdateModelMixin
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from rest_framework.views import APIView
from .models import  Cart, CartItem,Customer,Product,Collection,Waiter,RestaurantTable,TableReservation
from .serializers import CartSerializer,CartItemSerializer,AddCartItemSerializer, UpdateCartItemSerializer,CustomerSerializer,ProductSerializer,CollectionSerializer,CreateOrderSerializer,WaiterSerializer,RestaurantTableSerializer,TableReservationSerializer
from rest_framework.permissions import AllowAny, DjangoModelPermissions, DjangoModelPermissionsOrAnonReadOnly, IsAdminUser, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import ProductFilter
from .pagination import DefaultPagination
from .permissions import FullDjangoModelPermissions, IsAdminOrReadOnly,IsUserCustomer,IsUserOwner,IsUserWaiter
from django.db.models.aggregates import Count
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination    
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']
    permission_classes = [IsAuthenticated | IsUserOwner] 

    def get_permissions(self):
        if self.action == 'list': 
            return []
        return super().get_permissions()

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(
        products_count=Count('products')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAuthenticated | IsUserOwner] 

    def get_permissions(self):
        if self.action == 'list':  
            return []
        return super().get_permissions()

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']).exists():
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)


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
    
    def get_permissions(self):    
        if self.action == 'me':
            return [IsUserWaiter()]
        else:
            return super().get_permissions()



    
class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE','GET']:
            return [IsAdminUser()]
        return [IsUserCustomer()]
    


    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(
            data=request.data,
            context={'user_id': self.request.user.id})
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

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.all()

        customer_id = Customer.objects.only(
            'id').get(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id)   



class RestaurantTableView(ModelViewSet):
    queryset = RestaurantTable.objects.all()
    serializer_class = RestaurantTableSerializer
    permission_classes = [IsAuthenticated, IsUserOwner]

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
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except RestaurantTable.DoesNotExist:
            return Response({"error": "Restaurant table does not exist."}, status=status.HTTP_404_NOT_FOUND)




class TableReservationView(ModelViewSet):
    queryset = TableReservation.objects.all()
    serializer_class = TableReservationSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        reservation = self.get_object()
        user = request.user
        if IsUserOwner().has_permission(request, self) or IsUserWaiter().has_permission(request, self) or reservation.customer.user == user:
            return super().update(request, *args, **kwargs)
        else:
            return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        reservation = self.get_object()
        user = request.user
        if IsUserOwner().has_permission(request, self) or IsUserWaiter().has_permission(request, self) or reservation.customer.user == user:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)