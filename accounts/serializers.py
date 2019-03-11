from .models import UserProfile
from rest_framework import serializers

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('profile_id','user_id', 'displayName')
