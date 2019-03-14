from django import forms
from .models import UserProfile
from .models import Post, Comment, Follow
from django.forms.widgets import HiddenInput

class EditProfileForm(forms.ModelForm):
    # model that is linked to
    class Meta:
        model = UserProfile
        fields = [
                 'displayName',
                 'bio',
                 'host',
                 'github',
                 'url'
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
                'publish_time',
                'visibility',
                'unlisted'
                ]
    def __init__(self, *args, **kwargs):
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
