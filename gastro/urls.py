from django.urls import path
from gastro import views
urlpatterns = [
    path('', views.PersonList.as_view()),
    path('<int:pk>/', views.PersonDetail.as_view())
]