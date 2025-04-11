from django.urls import path
from .views import number_handler

urlpatterns = [
    path('<str:number_type>', number_handler),  # captures /numbers/e or /numbers/p etc.
]
