# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.urls import reverse_lazy
from django.views import generic

from .models import UserProfile, Post, Follow, FriendRequest, Comment

from django.contrib.auth.models import User

from .serializers import UserSerializers, PostSerializer, FollowSerializer, FriendRequestSerializer

from rest_framework.decorators import api_view

from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView

from .forms import NewPostForm, CreateComment,EditProfileForm#, FriendRequest
from django.shortcuts import get_list_or_404, get_object_or_404
from django.http import HttpResponseRedirect

def home(request):
    postList = Post.objects.all()
    # TODO filter posts in such a way that we can see only the ones we need
    commentList = Comment.objects.all()

    if request.user.is_authenticated:
        profile = UserProfile.objects.filter(user_id = request.user).first()
        context = {'list': postList, 'clist': commentList, 'userprofile_id': profile.author_id}
    else:
        context = {'list': postList, 'clist': commentList}
    return render(request, 'home.html', context)


@api_view()
def friend_list(request):
    # the currently authenticated user
    user = UserProfile.objects.filter(user_id = request.user).first()

    # all the people the current user is following
    following_list = Follow.objects.filter(follower_id = user.author_id).all()
    following_list_serial = FollowSerializer(following_list, many=True)
    following_id_list = list(following_list_serial.data[i]['following_id'] for i in range(len(following_list_serial.data)))

    # all the people who follow the current user
    follower_list = Follow.objects.filter(following_id = user.author_id).all()
    follower_list_serial = FollowSerializer(follower_list, many=True)
    follower_id_list = list(follower_list_serial.data[i]['follower_id'] for i in range(len(follower_list_serial.data)))

    # this is a list of the author_ids of all friends of the currently authenticated user
    friend_list = list(set(following_id_list) & set(follower_id_list))

    # a list of author objects of the friends
    friends = list()
    context = {'flist': friends}

    # populate the list of friends with the json of the authors
    for author_id in friend_list:
        f = UserProfile.objects.filter(author_id = author_id).first()
        friends.append(UserSerializers(f).data)

    return render(request,'friends.html', context)

class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

class UserViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializers

class UnFollow(APIView):
    def post(self, request, pk):
        print("------------------------")
        obj = Follow.objects.get(pk=pk)
        obj.delete()
        return redirect('/')

class FriendRequest(APIView):
    """
    post:
    Make a friend request
    """
    def post(self, request):
        # follow = Follow.objects.create()
        print(request)
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
        #here author_id is a displayname, we may change it later!!!
        thisUser = UserProfile.objects.filter(user_id = request.user).first()
        #user1 = UserProfile.objects.filter(user_id)
        postUser = UserProfile.objects.filter(displayName = author_id).first()
        author_id1 = thisUser.author_id
        author_id2 = postUser.author_id
        print(thisUser)
        print(postUser)
        print(author_id)
        is_following = Follow.objects.filter(follower_id = author_id1, following_id = author_id2).first()
        print(is_following)
        args = {'userprofile':postUser,'thisUser': thisUser, 'is_following': is_following} # pass in the whole user object
        return render(request, 'profile.html', args)


class PostById(APIView):
    """
    get:
    Get post for given {post_id}
    """
    def get(self, request, post_id):
        post = Post.objects.filter(post_id = post_id).first()
        comment = Comment.objects.filter(comment_id = comment_id).first()
        serializer = PostSerializer(post, comment)
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

class Comments(APIView):
    """
    get:
    return all comments for a given {post_id}

    post:
    create new comment on {post_id}

    """
    # def get(self, request, post_id):
        # comments = Comment.objects.filter(post_id = post_id)
        # serializer = CommentSerializer(comments, many=True)
        # return Response(serializer.data)

    def post(self, request, post_id):
        form = CreateComment(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
        return redirect('/')

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
        userprofile = UserProfile.objects.filter(user_id = request.user).first()
        if request.method == "POST":
            form = NewPostForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('/')
        else:
            profile_id = UserProfile.objects.filter(user_id = request.user).first()
            post_form = NewPostForm(initial={'user_id': profile_id})
            args = {'userprofile':userprofile,
                    'post_form':post_form} # pass in the whole user object
            return render(request, 'post.html', args)
    else:
        return redirect('/')
