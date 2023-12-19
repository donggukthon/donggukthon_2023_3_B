from rest_framework import serializers
from .models import *

class FishbreadSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Fishbread
        fields = ['name', 'price', 'day', 'isDonated']

class FishbreadTypeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(read_only=True)
    def get_image(self, instance):
        price = instance.fishbreads.first().price
        if price >= 3000:  # Example condition based on the price field, adjust as needed
            return instance.image1.url
        elif price >= 1000:
            return instance.image2.url
        else:
            return instance.image3.url
        
    class Meta:
        model = FishbreadType
        fields = ['name', 'image']