from .models import UserProfile
from .models import Post
from .models import FriendRequest
from .models import Follow
from rest_framework import serializers

from drf_extra_fields.fields import Base64ImageField
from drf_extra_fields.fields import Base64FileField

# Reference: django rest framework documentation
# https://www.django-rest-framework.org

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('author_id', 'displayName', 'host')


class PostSerializer(serializers.ModelSerializer):
    #user_id = serializers.HiddenField(default=self.get_serializer_context())
    image64 = Base64ImageField(required=False)
    file64 = Base64FileField(required=False)

    class Meta:
        model = Post
        fields = ('post_id', 'title', 'source', 'origin', 'description', 'contentType',
        'user_id', 'content', 'visibility', 'category', 'image64', 'file64', 'refPost')
        #read_only_fields = ('user_id',)


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
