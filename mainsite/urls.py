from django.urls import path
from .views import index, details

urlpatterns = [
    path('', index, name='home_page'),
    path('<slug:slug>/details', details, name='product_details'),
]
