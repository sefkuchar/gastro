from django.urls import path
from gastro import views
urlpatterns = [
    path('people', views.PersonList.as_view()),
    path('person/<int:pk>/', views.PersonDetail.as_view()),
    path('restaurants', views.RestaurantList.as_view()),
    path('restaurants/<int:pk>/', views.PersonDetail.as_view()),
    path('tablegrids', views.TableGridList.as_view()),
    path('tablegrid/<int:pk>/', views.TableGridDetail.as_view()),
    path('reservations', views.ReservationList.as_view()),
    path('reservation/<int:pk>/', views.ReservationDetail.as_view()),
    path('tables', views.TableList.as_view()),
    path('tables/<int:pk>/', views.TableDetail.as_view()),
    path('orders', views.OrderList.as_view()),
    path('orders/<int:pk>/', views.OrderDetail.as_view())
]