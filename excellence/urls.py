from django.contrib import admin
from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', index, name='index'),
    path('about/', about, name='about-us'),
    path('properties/', properties, name='properties'),
    path('estate/<int:pk>/', estate_detail, name='estate_detail'),
    path('estate/<int:pk>/update-location/', update_location, name='update_location'),
    path('estate/<int:pk>/edit/', edit_estate, name='edit_estate'),
    path('upload_property/', upload_property, name='upload_property'),
    path('estate/<int:pk>/edit/', edit_estate, name='edit_estate'),
    path('registration/register/', register, name='register'),
    path('contact/', contact, name='contact'),
    path('profile/', profile, name='profile'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)