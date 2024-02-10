from django.urls import path
from gastro import views
from rest_framework_nested import routers




router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet)
router.register('customers',views.CustomerViewSet)
router.register('waiters',views.WaiterViewSet)
router.register('tables',views.RestaurantTableView, basename='tables')
router.register('reservations',views.TableReservationView,basename='reservations')
router.register('carts',views.CartViewSet)
router.register('orders', views.OrderViewSet, basename='orders')


carts_router = routers.NestedDefaultRouter(router,'carts',lookup='cart')
carts_router.register('items',views.CartItemViewSet,basename='cart-items')


urlpatterns = router.urls + carts_router.urls