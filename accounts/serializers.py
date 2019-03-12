from .models import UserProfile
from .models import Post
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
