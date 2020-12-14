from django.urls import path
from .views import index, details, feedback, add_to_card, delete_from_card, change_order_count, get_pdf

urlpatterns = [
    path('', index, name='home_page'),
    path('get_pdf', get_pdf, name='get_pdf'),
    path('change_order_count/<int:order_id>', change_order_count, name='change_order_count'),
    path('add_to_cart/<slug:slug>', add_to_card, name='add_to_card'),
    path('delete_from_card/<slug:slug>', delete_from_card, name='delete_from_card'),
    path('feedback', feedback, name='feedback'),

    path('product/<slug:slug>/details', details, name='product_details'),
]
