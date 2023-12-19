from rest_framework import serializers
from .models import User
from fishbread.models import Fishbread
from fishbread.serializers import FishbreadSerializer
from badge.serializers import BadgeSerializer

# 붕어빵 제작 
class FishbreadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fishbread
        fields = ['charity', 'price', 'start_day', 'end_day', 'isDonated', 'fishbreadtype', 'user']


class UserBankSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields=['holder','bankname','account_num']

class UserDateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['date']

# 마이 페이지
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields= ['email', 'name','holder','bankname','account_num', 'date']

# 유저가 가진 붕어빵 
class UserFishbreadSerializer(serializers.ModelSerializer):
    fishbread = serializers.SerializerMethodField(read_only=True)
    def get_fishbread(self, instance):
        fishbread = instance.fishbread.filter(isDonated=False).first()
        serializer = FishbreadSerializer(fishbread)
        return serializer.data
                
    class Meta:
        model = User
        fields = ['fishbreadtype']


class FishbreadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fishbread
        fields = ['charity', 'price', 'start_day', 'end_day', 'isDonated', 'fishbreadtype']


class UserBadgeSerializer(serializers.ModelSerializer):
    badges = serializers.SerializerMethodField(read_only=True)
    def get_badges(self, instance):
        badges = instance.badge.all()
        if badges.exists():
            serializer = BadgeSerializer(badges, many=True)
            return serializer.data
        return None
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data['badges'] is None:
            del data['badges']
        return data

    class Meta:
        model = User
        fields = ['badges']