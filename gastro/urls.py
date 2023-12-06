from django.urls import path
from gastro import views
urlpatterns = [
    path('person', views.PersonList.as_view()),
    path('<int:pk>/', views.PersonDetail.as_view()),
    path('restaurant', views.RestaurantList.as_view()),
    path('<int:pk>/', views.RestaurantDetail.as_view())
]