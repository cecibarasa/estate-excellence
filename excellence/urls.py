from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('about/', about, name='about-us'),
    path('properties/', properties, name='properties'),
    path('estate/<int:pk>/', estate_detail, name='estate_detail'),
    path('upload_property/', upload_property, name='upload_property'),
    path('contact/', contact, name='contact-us'),

]