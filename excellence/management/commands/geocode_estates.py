from django.core.management.base import BaseCommand
from django.db.models import Q
from excellence.models import Estate
from geopy.geocoders import Nominatim
from decimal import Decimal

class Command(BaseCommand):
    help = 'Geocode estates missing latitude or longitude using Nominatim'

    def handle(self, *args, **options):
        qs = Estate.objects.filter(Q(latitude__isnull=True) | Q(longitude__isnull=True))
        total = qs.count()
        self.stdout.write(f'Found {total} estates with missing coordinates')
        geolocator = Nominatim(user_agent='estate_excellence_geocoder')
        for estate in qs:
            before = (estate.latitude, estate.longitude)
            # prefer exact_address, else fall back to location_name
            query = estate.exact_address if estate.exact_address else (f"{estate.location_name}, Kenya" if estate.location_name else '')
            if not query:
                self.stdout.write(self.style.WARNING(f'Skipping {estate.pk}: no address or location_name to geocode'))
                continue

            try:
                self.stdout.write(f'Geocoding {estate.pk}: "{query}"')
                location = geolocator.geocode(query, timeout=10)
                if location:
                    try:
                        estate.latitude = Decimal(str(round(location.latitude, 6)))
                        estate.longitude = Decimal(str(round(location.longitude, 6)))
                    except Exception:
                        estate.latitude = location.latitude
                        estate.longitude = location.longitude
                    estate.save()
                    after = (estate.latitude, estate.longitude)
                    self.stdout.write(self.style.SUCCESS(f'Geocoded {estate.pk} -> {after}'))
                else:
                    self.stdout.write(self.style.WARNING(f'No result from geocoder for {estate.pk} (query: "{query}")'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error geocoding {estate.pk} (query: "{query}") -> {e}'))
        self.stdout.write(self.style.NOTICE('Done.'))
