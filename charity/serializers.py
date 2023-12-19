from rest_framework import serializers
from .models import *

class CharitySerializer(serializers.ModelSerializer):
    # count = serializers.SerializerMethodField(read_only=True)
    # def get_count(self, obj):
    #     return obj.fishbread.all().count()

    class Meta:
        model = Charity
        fields = ['id', 'name', 'content', 'count']