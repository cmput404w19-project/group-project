from .models import UserProfile
from .models import Post
<<<<<<< HEAD
from .models import FriendRequest
=======
>>>>>>> f425a4072c4cc4669aa12426d5a826ee0505f06b
from .models import Follow
from rest_framework import serializers

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('author_id', 'displayName', 'host')


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('post_id', 'title', 'source', 'origin', 'description',
                'contentType', 'content', 'author_id', 'visibility')

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('requestedBy_id', 'requestedTo_id', 'request_status')

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('Follower', 'Following')
