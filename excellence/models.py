from django.db import models
from geopy.geocoders import Nominatim
from django.core.exceptions import ValidationError
from decimal import Decimal

# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    is_staff = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Agent(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()

    def __str__(self):
        return self.first_name

    def save_resident(self):
        self.save()    

    class Meta:
        ordering = ['first_name']

class Estate(models.Model):
    LOCATIONS = (
        ('Westlands', 'Westlands'), ('Parklands', 'Parklands'), ('Kilimani', 'Kilimani'),
        ('Machakos', 'Machakos'), ('Nakuru', 'Nakuru'), ('Kisumu', 'Kisumu'),
        ('Bungoma', 'Bungoma'), ('Ruaka', 'Ruaka'), ('Ruiru', 'Ruiru'),
        ('Kibera', 'Kibera'), ('Kitengela', 'Kitengela'), ('Athi River', 'Athi River'),        
        ('Thika', 'Thika'), ('Syokimau', 'Syokimau'), ('Utawala', 'Utawala'),
        ('Kasarani', 'Kasarani'), ('Ngong', 'Ngong'), ('Embu', 'Embu'),
        ('Runda', 'Runda'), ('Voi', 'Voi'), ('Komarock', 'Komarock'), 
        ('Donholm', 'Donholm'), ('Kileleshwa', 'Kileleshwa'), ('Mombasa', 'Mombasa'),       
    )
    name = models.CharField(max_length=100, default='', blank=True)
    image = models.ImageField(upload_to='excellence/photos/', blank=True)
    google_drive_image = models.ImageField(upload_to='excellence/google_drive_imports/', blank=True, null=True)
    description = models.TextField(max_length=500, blank=True)
    location_name = models.CharField(max_length=100, choices=LOCATIONS)
    bedrooms = models.PositiveIntegerField(default=0, blank=True)
    bathrooms = models.PositiveIntegerField(default=0, blank=True)
    total_built_area = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    plot_size = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    garage = models.IntegerField(default=False)
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    amenities = models.TextField(blank=True, default='')
    year = models.DateTimeField(auto_now_add=True)
    
    # This text field will be converted into our Google Autocomplete search input
    exact_address = models.CharField(
        max_length=300, 
        help_text="e.g., Fedha Estate, Court 4, Plot 12", blank=True
    )
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        ordering = ['-pk']

    def update_exact_address_from_coordinates(self):
        if self.latitude is None or self.longitude is None:
            return

        try:
            geolocator = Nominatim(user_agent='estate_excellence_geocoder')
            location = geolocator.reverse((float(self.latitude), float(self.longitude)), language='en', exactly_one=True)
            if not location:
                self.exact_address = self.exact_address or self.location_name or 'Location unavailable'
                return

            address = location.raw.get('address', {}) if hasattr(location, 'raw') else {}
            parts = []
            if address.get('house_number'):
                parts.append(address.get('house_number'))
            if address.get('road'):
                parts.append(address.get('road'))
            if address.get('neighbourhood'):
                parts.append(address.get('neighbourhood'))
            if address.get('suburb'):
                parts.append(address.get('suburb'))
            if address.get('town'):
                parts.append(address.get('town'))
            elif address.get('city'):
                parts.append(address.get('city'))
            elif address.get('village'):
                parts.append(address.get('village'))
            if address.get('state'):
                parts.append(address.get('state'))
            if address.get('country'):
                parts.append(address.get('country'))

            if parts:
                self.exact_address = ', '.join(parts)
            else:
                self.exact_address = self.exact_address or self.location_name or 'Location unavailable'
        except Exception:
            self.exact_address = self.exact_address or self.location_name or 'Location unavailable'

    def save(self, *args, **kwargs):
        # If coordinates are missing, try to geocode from the exact address
        # or fallback to the selected location name (biased to Kenya).
        try:
            if (self.latitude is None or self.longitude is None) and (self.exact_address or self.location_name):
                geolocator = Nominatim(user_agent='estate_excellence_geocoder')
                query = self.exact_address if self.exact_address else f"{self.location_name}, Kenya"
                location = geolocator.geocode(query, timeout=10)
                if location:
                    # store with 6 decimal places
                    try:
                        self.latitude = Decimal(str(round(location.latitude, 6)))
                        self.longitude = Decimal(str(round(location.longitude, 6)))
                    except Exception:
                        # Fallback to raw floats if Decimal conversion fails
                        self.latitude = location.latitude
                        self.longitude = location.longitude

            if not self.exact_address and self.location_name:
                self.exact_address = self.location_name
        except Exception:
            # Don't block save on geocoding failures; silently continue
            pass

        super().save(*args, **kwargs)

    @property
    def display_location(self):
        return self.exact_address or self.location_name or 'Location unavailable'

    def __str__(self):
        return self.name


    

class Contact(models.Model):
    name= models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    date = models.DateField()