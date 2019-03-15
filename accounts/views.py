# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.urls import reverse_lazy
from django.views import generic

from .models import *

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

from rest_framework.renderers import TemplateHTMLRenderer

import copy

def home(request):
    postList = []
    if request.user.is_authenticated:
        # postList = Post.objects.all()
        user = UserProfile.objects.filter(user_id = request.user).first()
        # TODO filter posts in such a way that we can see only the ones we need
        # All post that can see
        # PUBLIC post
        public_post = Post.objects.filter(visibility="PUBLIC").all()
        for post in public_post:
            postList.append({"p":post})
        # users own post
        own_post = Post.objects.filter(user_id=user.author_id).exclude(visibility="PUBLIC").all()
        for post in own_post:
            postList.append({"p":post})
        # see friends post  (private to friends)
        # get a list of friends userprofile object
        friends_userprofile = find_friends(user)
        for friend in friends_userprofile:
            # get all the friends private post
            friendPrivatePosts = Post.objects.filter(visibility="FRIENDS", user_id=friend).all()
            for post in friendPrivatePosts:
                postList.append({"p":post})
        # see friends post's that is visible to me (private to certain users, and I am one of them who can see it)
        all_visible_post_object = PostVisibleTo.objects.filter(user_id=user.author_id).all()
        for i in all_visible_post_object:
            post = Post.objects.filter(post_id=i.post_id.post_id).first()
            postList.append({"p":post})
        # see friends of friends post

        # see our own server's post

        # now get the comments(comment list) of each post that is visible to this user
        for post in postList:
            post["cl"] = Comment.objects.filter(post_id=post["p"].post_id).order_by("publish_time").all()



    # TODO we need a way to somehow get the comment objects for each specific post
    # and then add that list of comment objects to that post object
    # so that we can render the post and the comment belong to that post correctly
    if request.user.is_authenticated:
        profile = UserProfile.objects.filter(user_id = request.user).first()
        context = {'list': postList, 'userprofile_id': profile.author_id}
    else:
        context = {'list': postList}
    return render(request, 'home.html', context)



def find_friends(user):
    """
    This function will take in the userprofile object and find all the friends of the current user
    Input: request
    Return: a list of all friends userprofile object
    """

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

    return friend_list


@api_view()
def friend_list(request):

    # the currently authenticated user
    user = UserProfile.objects.filter(user_id = request.user).first()

    friendlist = find_friends(user)

    # a list of author objects of the friends
    friends = list()

    # populate the list of friends with the json of the authors
    for author_id in friendlist:
        f = UserProfile.objects.filter(author_id = author_id).first()
        friends.append(UserSerializers(f).data)
    context = {'flist': friends}
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
        #return render(request,'friend_requests.html', context)

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
        post = Post.objects.filter(post_id = post_id).all().first()
        commentList=[]
        comments = Comment.objects.filter(post_id = post_id).all()
        for comment in comments:
            commentList.append({"comment":comment})
        context = {'post': post, 'commentList': commentList}
        return render(request, 'showPost.html', context)

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
            return redirect('/#'+str(post_id))
        return redirect('/')


class AuthorPosts(APIView):
    """
    get:
    Get all posts visible to current user

    post:
    Create a new post as current user
    """
    renderer_classes = [TemplateHTMLRenderer]
    #model = Post
    template_name = '../templates/post.html'
    #fields = ['title', 'description','content', 'content-options', 'isibility-select']
    #login_url="/accounts/login/"

    def get(self, request):
        print(request.body)
        posts = Post.objects.all()
        serializer = PostSerializer()
        return Response({'serializer':serializer})

    def post(self, request):
        #profile = get_object_or_404(Profile, pk=pk)
        #print(request.data.user_id)
        new_data = request.data.copy()
        user_id = str(UserProfile.objects.filter(user_id = request.user).first().author_id)
        print(user_id)
        new_data.__setitem__("user_id", user_id)
        print(new_data)
        serializer = PostSerializer(data=new_data)
        print(serializer)

        if not serializer.is_valid():
            return Response({'serializer': serializer})
        serializer.save()
        return redirect('/')


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
