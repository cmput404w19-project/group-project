from django import forms
from .models import UserProfile
from .models import Post, Comment, Follow
from django.forms.widgets import HiddenInput

# Reference: Django custom form documentaiton
# https://docs.djangoproject.com/en/2.1/topics/forms/

class EditProfileForm(forms.ModelForm):
    # model that is linked to
    class Meta:
        model = UserProfile
        fields = [
                 'displayName',
                 'bio',
                 'github',
                ]

class NewPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
                'user_id',
                'title',
                'description',
                'source',
                'origin',
                'contentType',
                'content',
                'category',
                'published',
                'visibility',
                'unlisted'
                ]
    def __init__(self, *args, **kwargs):
        # Reference
        # https://www.itgank.com/archives/2557
        # https://stackoverflow.com/questions/604266/django-set-default-form-values
        super(NewPostForm, self).__init__(*args, **kwargs)
        self.fields['user_id'].widget = HiddenInput()

class CreateComment(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
                'user_id',
                'content',
                'post_id'
                ]
    def __init__(self, *args, **kwargs):
        super(CreateComment, self).__init__(*args, **kwargs)
        self.fields['user_id'].widget = HiddenInput()
        self.fields['post_id'].widget = HiddenInput()
