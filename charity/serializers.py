from rest_framework import serializers
from .models import *

class CharitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Charity
        fields = ['id', 'name', 'content', 'count']