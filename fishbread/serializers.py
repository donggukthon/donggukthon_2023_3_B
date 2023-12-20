from datetime import date

from .models import *

from rest_framework import serializers


class FishbreadSerializer(serializers.ModelSerializer):
    since = serializers.SerializerMethodField(read_only=True)
    def get_since(self, instance):
        today = date.today()
        start = instance.start_day
        return (today - start).days
    
    image = serializers.SerializerMethodField(read_only=True)
    def get_image(self, instance):
        price = instance.price
        if price >= 3000:  # Example condition based on the price field, adjust as needed
            return instance.fishbreadtype.image1.url
        elif price >= 1000:
            return instance.fishbreadtype.image2.url
        else:
            return instance.fishbreadtype.image3.url

    name = serializers.SerializerMethodField(read_only=True)
    def get_name(self, instance):
        name = instance.fishbreadtype.name
        return name

    class Meta:
        model = Fishbread
        fields = ['id', 'price', 'since', 'name', 'image']

class FishbreadTypeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(read_only=True)
    def get_image(self, instance):
        price = instance.fishbread.filter(isDonated=False).first().price
        if price >= 3000:  # Example condition based on the price field, adjust as needed
            return instance.image1.url
        elif price >= 1000:
            return instance.image2.url
        else:
            return instance.image3.url
        
    class Meta:
        model = FishbreadType
        fields = ['name', 'image']

class FishbreadHistorySerializer(serializers.ModelSerializer):
    charity = serializers.SerializerMethodField(read_only=True)
    def get_charity(self, instance):
        charitys = instance.charity.all()
        return [c.name for c in charitys]

    class Meta:
        model = Fishbread
        fields=['end_day', 'charity', 'price']
