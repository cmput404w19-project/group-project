# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.urls import reverse_lazy
from django.views import generic
from .models import UserProfile, Post
from django.contrib.auth.models import User
from .serializers import UserSerializers
from rest_framework import viewsets
from .forms import EditProfileForm


# Create your views here.
class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

class UserViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializers

def home(request):
    postList = Post.objects.all()
    context = {'list': postList}
    return render(request, 'home.html', context)
    
def profile(request):
	if request.user.is_authenticated:
		# user has login
		userprofile = UserProfile.objects.filter(user_id = request.user.id).first()
		args = {'userprofile':userprofile} # pass in the whole user object
		return render(request, 'profile.html', args)
	else:
		# not login yet
		return redirect('/')

def edit_profile(request):
	if request.user.is_authenticated:
		# user has login
		if request.method == "POST":
			userprofile = UserProfile.objects.filter(user_id = request.user).first()
			form = EditProfileForm(request.POST, instance=userprofile)
			if form.is_valid():
				form.save()

				# text = form.cleaned_data['displayName']
				return redirect('/accounts/profile')
		else:
			userprofile = UserProfile.objects.filter(user_id = request.user).first()
			form = EditProfileForm(instance=userprofile)
			args = {'form': form, 'userprofile': userprofile}
			return render(request, 'edit_profile.html', args)
	else:
		# not login yet
		return redirect('/')
