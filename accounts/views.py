# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.urls import reverse_lazy
from django.views import generic

from .models import UserProfile, Post

from django.contrib.auth.models import User

from .serializers import UserSerializers, PostSerializer,FollowSerializer

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView

from .forms import EditProfileForm
from .forms import NewPostForm

def home(request):
    postList = Post.objects.all()
    context = {'list': postList}
    return render(request, 'home.html', context)

class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

class UserViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializers

class AuthorProfile(APIView):
    def get(self, request, author_id):
        print(author_id)
        print(request.user)
        #here author_id is a displayname, we may change it later!!!
        thisUser = UserProfile.objects.filter(user_id = request.user).first()
        userprofile = UserProfile.objects.filter(displayName = author_id).first()
        args = {'userprofile':userprofile,'thisUser': thisUser} # pass in the whole user object
        return render(request, 'profile.html', args)

    def post(self, request, author_id):
        serializer = FollowSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostById(APIView):
    def get(self, request, post_id):
        post = Post.objects.filter(post_id = post_id).first()
        serializer = PostSerializer(post)
        return Response(serializer.data)

class PublicPosts(APIView):
    def get(self, request):
        posts = Post.objects.filter(visibility = "PUBLIC")
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

class AuthorPosts(APIView):
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def profile(request):
    # user has login
    userprofile = UserProfile.objects.filter(user_id = request.user.id).first()
    args = {'userprofile':userprofile} # pass in the whole user object
    return render(request, 'profile.html', args)
    


def edit_profile(request):
    # user has login
    if request.method == "POST":
        # POST
        userprofile = UserProfile.objects.filter(user_id = request.user).first()
        form = EditProfileForm(request.POST, instance=userprofile)
        if form.is_valid():
            form.save()

            # text = form.cleaned_data['displayName']
            return redirect('/accounts/profile')
    else:
        # GET
        userprofile = UserProfile.objects.filter(user_id = request.user).first()
        form = EditProfileForm(instance=userprofile)
        args = {'form': form, 'userprofile': userprofile}
        return render(request, 'edit_profile.html', args)
    

def post_page(request):
    if request.user.is_authenticated:
        # user has login
        userprofile = UserProfile.objects.filter(user_id = request.user.id).first()
        if request.method == "POST":
            form = NewPostForm(request.POST)
            if form.is_valid():
                #print(form)
                #form.instance.author_id = UserProfile.objects.filter(user_id = request.user.id).first().get_profile_id()
                form.save()
                # text = form.cleaned_data['displayName']
                return redirect('/')
        else:
            #print()
            #print(UserProfile.objects.filter(user_id = request.user.id).first().author_id)
            #print()
            profile_id = UserProfile.objects.filter(user_id = request.user.id).first()
            #post_form = forms.IntegerField(widget=forms.HiddenInput(), initial=123)
            post_form = NewPostForm(initial={'author_id': profile_id})
            args = {'userprofile':userprofile,
                    'post_form':post_form} # pass in the whole user object
            return render(request, 'post.html', args)
    else:
        return redirect('/')
