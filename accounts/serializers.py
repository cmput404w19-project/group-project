from .models import *
from rest_framework import serializers
from django.contrib.auth.models import User
from drf_extra_fields.fields import Base64ImageField
from drf_extra_fields.fields import Base64FileField
import datetime

# Reference: django rest framework documentation
# https://www.django-rest-framework.org

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('author_id', 'displayName', 'host')

class AuthorSerializers(serializers.ModelSerializer):
    id = serializers.SerializerMethodField('get_author_id')

    class Meta:
        model = UserProfile
        fields = ('id','host','displayName','url','github')
    def get_author_id(self, obj):
        return obj.author_id


class PostSerializer(serializers.ModelSerializer):
    #user_id = serializers.HiddenField(default=self.get_serializer_context())
    image64 = Base64ImageField(required=False)
    file64 = Base64FileField(required=False)

    class Meta:
        model = Post
        fields = ('post_id', 'title', 'source', 'origin', 'description', 'contentType',
        'user_id', 'content', 'visibility', 'category', 'image64', 'file64', 'refPost')
        #read_only_fields = ('user_id',)

class CommentSerializer(serializers.ModelSerializer):
    #comment = serializers.SerializerMethodField() # content
    id = serializers.SerializerMethodField('get_comment_id') #comment_id
    #author = serializers.SerializerMethodField() #user_id
    class Meta:
        model = Comment
        fields = ('user_id','content','contentType','published','id', 'post_id')
    '''
    def get_comment(self, obj):
        return obj.content
    '''

    def get_comment_id(self, obj):
        return obj.comment_id
    '''

    def get_author(self, obj):
        # just use this tmp not to change later
        user = User.objects.filter(username=obj.user_id).first()
        comment_author = UserProfile.objects.filter(user_id=user).first()
        return AuthorSerializers(comment_author).data
    '''
class GETProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('displayName','author_id','bio','host','github','url')



class GETCommentSerializer(serializers.ModelSerializer):
    comment = serializers.SerializerMethodField() # content
    id = serializers.SerializerMethodField('get_comment_id') #comment_id
    author = serializers.SerializerMethodField() #user_id

    class Meta:
        model = Comment
        fields = ('author','comment','contentType','published','id')
    
    def get_comment(self, obj):
        return obj.content

    def get_comment_id(self, obj):
        return obj.comment_id

    def get_author(self, obj):
        # just use this tmp not to change later
        user = User.objects.filter(username=obj.user_id).first()
        comment_author = UserProfile.objects.filter(user_id=user).first()
        return AuthorSerializers(comment_author).data




class GETPostSerializer(serializers.ModelSerializer):
    #user_id = serializers.HiddenField(default=self.get_serializer_context())
    image64 = Base64ImageField(required=False)
    file64 = Base64FileField(required=False)
    # Django rest framework documentation
    # https://www.django-rest-framework.org/api-guide/fields/#serializermethodfield
    # by default: it will call get_xxx()
    comments = serializers.SerializerMethodField()  # include the comments data into the post
    author = serializers.SerializerMethodField()  # include the author data into the post
    id = serializers.SerializerMethodField('get_post_id') # change the name in json

    class Meta:
        model = Post
        fields = ('id','title', 'author', 'source', 'origin', 'description', 'contentType',
         'content', 'visibility', 'category', 'image64', 'file64', 'refPost', 'unlisted', 'published','comments')
        #read_only_fields = ('user_id',)

    def get_comments(self, obj):
        post_comments = Comment.objects.filter(post_id=obj.post_id).order_by("published").all()
        return GETCommentSerializer(post_comments, many=True).data
    def get_author(self, obj):
        # just use this tmp not to change later
        user = User.objects.filter(username=obj.user_id).first()
        post_author = UserProfile.objects.filter(user_id=user).first()
        return AuthorSerializers(post_author).data
    def get_post_id(self, obj):
        return obj.post_id
    def get_publishTime(self, obj):
        # author: Aneesh R S  https://stackoverflow.com/users/4795365/aneesh-r-s
        # https://stackoverflow.com/questions/29796212/convert-django-datetime-format-to-template-type-formatting
        publishTime = Post.objects.filter(post_id=obj.post_id).first().published
        return publishTime.strftime('%b %d, %Y, %I:%M %p')

class PDFBase64File(Base64FileField):
    ALLOWED_TYPES = ['pdf']

    def get_file_extension(self, filename, decoded_file):
        try:
            PyPDF2.PdfFileReader(io.BytesIO(decoded_file))
        except PyPDF2.utils.PdfReadError as e:
            logger.warning(e)
        else:
            return 'pdf'


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('requestedBy_id', 'requestedTo_id', 'request_status')

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('follower_id', 'following_id')
