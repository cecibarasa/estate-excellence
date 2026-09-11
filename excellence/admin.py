# admin.py
from django.contrib import admin
from .models import *

@admin.register(Estate)
class EstateAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_name', 'exact_address', 'latitude', 'longitude')
    
    class Media:
        css = {
            'all': (
                'https://googleapis.com',
                'https://cloudflare.com',
                'https://cloudflare.com', # Search bar CSS
            )
        }
        js = (
            'https://cloudflare.com',
            'https://cloudflare.com', # Search bar Engine
            'js/admin_map_picker.js', # Our custom script file
        )
