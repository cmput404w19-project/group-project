from .models import UserProfile
from .models import Post
from .models import FriendRequest
from .models import Follow
from rest_framework import serializers

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('author_id', 'displayName', 'host')


class PostSerializer(serializers.ModelSerializer):
    #user_id = serializers.HiddenField(default=self.get_serializer_context())
    class Meta:
        model = Post
        fields = ('post_id', 'title', 'source', 'origin', 'description',
                'contentType', 'user_id', 'content', 'visibility', 'category')
        #read_only_fields = ('user_id',)


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('requestedBy_id', 'requestedTo_id', 'request_status')

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('follower_id', 'following_id')
