# accounts/views.py
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from .models import Post

# Create your views here.
class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


def home( request):
    postList = Post.objects.all()
    context = {'list': postList}
    return render(request, 'home.html', context)
    