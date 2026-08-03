from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('about/', about, name='about-us'),
    path('properties/', properties, name='properties'),
    path('contact/', contact, name='contact-us'),
]