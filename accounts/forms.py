from django import forms
from .models import UserProfile
from .models import Post
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
			'author_id',
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
		self.fields['author_id'].widget = HiddenInput()
