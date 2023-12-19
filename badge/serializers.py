from rest_framework import serializers
from .models import *

class BadgeSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True, required=False)

    class Meta:
        model = Badge
        fields = ['id', 'name', 'image']