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
    path('upload-image/<str:file_id>/', upload_image_from_drive, name='upload_image_from_drive'),
    path('google/login/', google_drive_login, name='google_drive_login'),
    path('google/callback/', google_callback, name='google_callback'),
    path('google/import/<str:file_id>/', google_drive_import, name='google_drive_import'),
    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)