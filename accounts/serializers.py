from .models import *
from rest_framework import serializers
from django.contrib.auth.models import User
from drf_extra_fields.fields import Base64ImageField
from drf_extra_fields.fields import Base64FileField
import datetime
from urllib import request
import json

# Reference: django rest framework documentation
# https://www.django-rest-framework.org

class PostSerializer(serializers.ModelSerializer):
    #user_id = serializers.HiddenField(default=self.get_serializer_context())
    # image64 = Base64ImageField(required=False)
    # file64 = Base64FileField(required=False)
    id = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    visibleTo = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    next = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    origin = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'source', 'origin', 'description', 'contentType',
        'author', 'content', 'visibility', 'categories', 'visibleTo', 'unlisted', 
        'count', 'size', 'next', 'comments', 'published', 'user_id', 'host')
        #read_only_fields = ('user_id',)

    def get_id(self, obj):
        return obj.post_id
    
    def get_author(self, obj):
        return GETProfileSerializer(obj.user_id).data

    def get_categories(self, obj):
        return obj.category.split()

    def get_count(self, obj):
        return len(Comment.objects.filter(post_id=obj.post_id).all())

    def get_size(self, obj):
        return None # TODO figure out what size should be determined by

    def get_next(self, obj):
        return str(obj.host) + 'posts/'+ str(obj.post_id) +'/comments'

    def get_comments(self, obj):
        return []

    def get_visibleTo(self, obj):
        return []

    def get_origin(self, obj):
        return str(obj.host) + 'posts/' + str(obj.post_id)

    def get_source(self, obj):
        return str(obj.host) + 'posts/' + str(obj.post_id)


class GETProfileSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField('get_author_id')
    class Meta:
        model = UserProfile
        fields = ('displayName','id','bio','host','github','url')

    def get_author_id(self, obj):
        if type(obj) == dict:
            return str(obj['host']) + '/author/' + str(obj['author_id'])
        return str(obj.host) + '/author/' + str(obj.author_id)


class CommentSerializer(serializers.ModelSerializer):
    #comment = serializers.SerializerMethodField() # content
    #id = serializers.SerializerMethodField('get_comment_id') #comment_id
    #author = serializers.SerializerMethodField() #user_id url
    class Meta:
        model = Comment
        fields = ('user_id','content','contentType', 'post_id')

    def get_comment_id(self, obj):
        return obj.comment_id
    '''
    def get_author(self, obj):
        # just use this tmp not to change later
        user = User.objects.filter(username=obj.user_id).first()
        comment_author = UserProfile.objects.filter(user_id=user).first()
        return AuthorSerializers(comment_author).data
    '''

class GETCommentSerializer(serializers.ModelSerializer):
    comment = serializers.SerializerMethodField() # content
    id = serializers.SerializerMethodField('get_comment_id') #comment_id
    author = serializers.SerializerMethodField() #user_id

    class Meta:
        model = Comment
        fields = ('author','comment','contentType','published','id', 'post_id')
    
    def get_comment(self, obj):
        return obj.content

    def get_comment_id(self, obj):
        return obj.comment_id

    def get_author(self, obj):
        # Reference:
        # https://www.kancloud.cn/thinkphp/python-guide/39426
        #user = User.objects.filter(username=obj.user_id).first()
        with request.urlopen(obj.user_id) as f:
            data = f.read().decode('utf-8')
            data = json.loads(data)
            return data

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('requestedBy_name','requestedBy_url', 'requestedTo_url', 'request_status')

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('follower_url', 'following_url')

class ExternalServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalServer
        fields = ('server_url', 'user', 'password')

