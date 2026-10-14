from django.contrib.postgres import serializers
from .models import *
from rest_framework import serializers


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estate
        fields = ['google_drive_image']