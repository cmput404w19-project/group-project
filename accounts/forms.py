from django import forms
from .models import UserProfile

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