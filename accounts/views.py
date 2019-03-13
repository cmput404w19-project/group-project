# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.urls import reverse_lazy
from django.views import generic

from .models import UserProfile, Post, Follow, FriendRequest

from django.contrib.auth.models import User

from .serializers import UserSerializers, PostSerializer, FollowSerializer, FriendRequestSerializer

from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView

from .forms import EditProfileForm

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

class FriendRequest(APIView):
    """
    post:
    Make a friend request
    """
    def post(self, request):
        # follow = Follow.objects.create()
        data = dict()
        data['requestedBy_id'] = request.data['author']['id'].split('/')[-1]
        data['requestedTo_id'] = request.data['friend']['id'].split('/')[-1]
        data['follower_id']=request.data['author']['id'].split('/')[-1]
        data['following_id']=request.data['friend']['id'].split('/')[-1]
        friend_request_serializer = FriendRequestSerializer(data=data)
        follow_serializer = FollowSerializer(data=data)
        
        failed = 0

        if friend_request_serializer.is_valid():
            friend_request_serializer.save()
        else:
            failed = 1

        if follow_serializer.is_valid():
            follow_serializer.save()
        else:
            return Response(follow_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if failed:
            return Response(friend_request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({ "query": "friendrequest", "success": True, "message": "Friend request sent" }, status=status.HTTP_200_OK)

class AuthorProfile(APIView):
    """
    get:
    Get the profile for a given {author_id}
    """
    def get(self, request, author_id):
        userprofile = UserProfile.objects.filter(user_id = request.user.id).first()
        args = {'userprofile':userprofile} # pass in the whole user object
        return render(request, 'profile.html', args)

class PostById(APIView):
    """
    get:
    Get post for given {post_id}
    """
    def get(self, request, post_id):
        post = Post.objects.filter(post_id = post_id).first()
        serializer = PostSerializer(post)
        return Response(serializer.data)

class PublicPosts(APIView):
    """
    get:
    Get all public posts on server
    """
    def get(self, request):
        posts = Post.objects.filter(visibility = "PUBLIC")
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


class AuthorPosts(APIView):
    """
    get:
    Get all posts visible to current user

    post:
    Create a new post as current user
    """
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
    if request.user.is_authenticated:
        # user has login
        userprofile = UserProfile.objects.filter(user_id = request.user.id).first()
        print(user_id)
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
