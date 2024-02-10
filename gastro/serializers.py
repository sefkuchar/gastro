from rest_framework import serializers
from .models import Cart, CartItem,Product,Customer,Waiter,Collection,OrderItem,Order,RestaurantTable, TableReservation
from decimal import Decimal
from core.models import User
class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','title','unit_price']

    
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug',
                  'unit_price', 'price_with_tax', 'collection']

    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

    products_count = serializers.IntegerField(read_only=True)


class CartItemSerializer(serializers.ModelSerializer):  
    product = SimpleProductSerializer()
    total_price  = serializers.SerializerMethodField()

    def get_total_price(self,cart_item:CartItem):
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = CartItem
        fields = ['id','product','quantity','total_price']

class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True,read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self,cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])


    class Meta:
        model = Cart
        fields = ['id','items','total_price']

class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self,val):
        if not Product.objects.filter(pk=val).exists():
            raise serializers.ValidationError('No product with the given Id was found')
        return val
    def save(self,**kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(cart_id =  cart_id,product_id = product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance =    CartItem.objects.create(cart_id = cart_id,**self.validated_data)    
        return self.instance


    class Meta:
        model = CartItem
        fields = ['id','product_id','quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model =  CartItem
        fields = ['quantity']

class CustomerSerializer(serializers.ModelSerializer):  
    user_id = serializers.IntegerField()

    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone']

    def validate_user_id(self, value):
        try:
            
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user with the given ID exists.")
        
        if Customer.objects.filter(user_id=value).exists():
            raise serializers.ValidationError("Customer with the given user ID already exists.")

        return value

class WaiterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waiter
        fields = ['id','user_id','restaurant_id']


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'unit_price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'items']


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError(
                'No cart with the given ID was found.')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('The cart is empty.')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']

            customer = Customer.objects.get(
                user_id=self.context['user_id'])
            order = Order.objects.create(customer=customer)

            cart_items = CartItem.objects \
                .select_related('product') \
                .filter(cart_id=cart_id)
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity
                ) for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(pk=cart_id).delete()

            order_created.send_robust(self.__class__, order=order)

            return order


class RestaurantTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantTable
        fields = ['id', 'restaurant', 'seats', 'row', 'column', 'table_status']

    def create(self, validated_data):
        restaurant_id = validated_data.get('restaurant').id
        row = validated_data.get('row')
        column = validated_data.get('column')
        
        existing_table = RestaurantTable.objects.filter(restaurant_id=restaurant_id, row=row, column=column).first()
        if existing_table:
            raise serializers.ValidationError("A table with the same restaurant id, row, and column already exists.")

        return super().create(validated_data)


class TableReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableReservation
        fields = ['id', 'customer', 'table', 'date_time_from', 'date_time_to']

    def create(self, validated_data):
        
        table_id = validated_data.get('table').id
        date_time_from = validated_data.get('date_time_from')
        date_time_to = validated_data.get('date_time_to')
        
        existing_reservation = TableReservation.objects.filter(table_id=table_id, date_time_from=date_time_from, date_time_to=date_time_to).first()
        if existing_reservation:
            raise serializers.ValidationError("A reservation with the same table and time already exists.")

        return super().create(validated_data)        