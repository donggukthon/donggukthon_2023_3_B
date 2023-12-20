from rest_framework import serializers
from .models import User
from badge.models import Badge
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
    
    def update(self, instance, validated_data):
        date = validated_data.get('date', instance.date)

        instance.date = ','.join(map(str, date))
        # instance.date = ','.join(date_list)
        instance.save()

        return instance

# 마이 페이지
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields= ['email', 'name','holder','bankname','account_num', 'date']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            # name = validated_data['name'],
            email = validated_data['email'],
            password = validated_data['password']
        )
        return user

# 유저가 가진 붕어빵 
class UserFishbreadSerializer(serializers.ModelSerializer):
    fishbreads = serializers.SerializerMethodField(read_only=True)
    def get_fishbreads(self, instance):
        fishbread = instance.fishbreads.filter(isDonated=False).first()
        serializer = FishbreadSerializer(fishbread)
        return serializer.data
                
    class Meta:
        model = User
        fields = ['fishbreads']

class FishbreadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fishbread
        fields = ['charity', 'price', 'start_day', 'end_day', 'isDonated', 'fishbreadtype']

class UserBadgeSerializer(serializers.ModelSerializer):
    badges = serializers.SerializerMethodField()

    def get_badges(self, instance):
        user_badge_ids = set(instance.badge.values_list('id', flat=True))
        all_badges = Badge.objects.all()

        serialized_badges = []
        for badge in all_badges:
            badge_data = {
                'id': badge.id,
                'image': badge.image1.url if badge.id in user_badge_ids else badge.image2.url
            }
            serialized_badges.append(badge_data)

        return serialized_badges

    class Meta:
        model = User
        fields = ['badges',]
