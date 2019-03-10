# accounts/views.py
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from .models import UserProfile, Post
from django.contrib.auth.models import User
from .serializers import UserSerializers
from rest_framework import viewsets

# Create your views here.
class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

class UserViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializers

def home( request):
    postList = Post.objects.all()
    context = {'list': postList}
    return render(request, 'home.html', context)
    
def profile(request):
	args = {'user':request.user} # pass in the whole user object
	print(request.user)
	return render(request, 'profile.html', args)
