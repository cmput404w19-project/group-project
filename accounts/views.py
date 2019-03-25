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

from django.http import HttpResponseNotFound

DEBUG = False 

# Reference: Django class-based view
# https://docs.djangoproject.com/en/2.1/topics/class-based-views/

def home(request):
    # so right now we decide to use javacript to get all the posts and comments data
    # and render stuff in the client side

    context = {} # this will be the dictionary format of all data that pass into the html before return to clients

    # Things that need to pass into the html
    # -userprofile
    # -post api url 

    # check for basic token auth (Django built-in)
    if request.user.is_authenticated:
        # check if we actually have this user 
        # if not return 404
        if len(User.objects.filter(id=request.user.id)) != 1:
            return HttpResponseNotFound("The user information is not found")         
        # get userprofile information
        context["userprofile"] = UserProfile.objects.filter(user_id=request.user).first()
        # since this is our server, no need domain name for the url just the path
        # so this will be our post api path
        context["author_post_api_url"] = "/author/posts"  # this path url should handle to get all posts that is visible for this user

        return render(request, 'home.html', context)


    else:
        # not login 
        return render(request, 'landingPage.html')


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
        obj = Follow.objects.get(pk=pk)
        name = obj.following_id.author_id
        #print(name)
        obj.delete()
        return redirect('/author/' + str(name))

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
        # now the author_id is uuid
        thisUser = UserProfile.objects.filter(user_id = request.user).first()
        postUser = UserProfile.objects.filter(author_id = author_id).first()
        author_id1 = thisUser.author_id
        author_id2 = postUser.author_id
        if DEBUG:
            print(thisUser)
            print(postUser)
            print(author_id)
        is_following = Follow.objects.filter(follower_id = author_id1, following_id = author_id2).first()
        if DEBUG:
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


class postDelete(APIView):
    #delete post
    #referenced answered by cutteeth from https://stackoverflow.com/questions/40191931/django-how-to-use-request-post-in-a-delete-view
    def post(self, request, post_id):
        obj = Post.objects.filter(post_id=post_id).first()
        obj.delete()
        return redirect('/')


class EditPost(APIView):

    def get(self, request, post_id):
        post = Post.objects.filter(post_id = post_id).first()
        context = {'post': post}
        return render(request, 'editpost.html', context)

    def post(self, request, post_id):
        new_data = request.data.copy()
        post = Post.objects.filter(post_id = post_id).first()
        user_id = str(UserProfile.objects.filter(user_id = request.user).first().author_id)
        new_data.__setitem__("user_id", user_id)
        serializer = PostSerializer(post, data=new_data)

        if not serializer.is_valid():
            return Response({'serializer': serializer})
        serializer.save()
        return redirect('/')

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
        form = CreateComment(data=request.POST)
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
    # renderer_classes = [TemplateHTMLRenderer]
    #model = Post
    # template_name = '../templates/post.html'
    #fields = ['title', 'description','content', 'content-options', 'isibility-select']
    #login_url="/accounts/login/"

    def get(self, request):
        print(request.body)
        print("get the GET request")
        posts = Post.objects.all()
        serializer = PostSerializer()
        return Response({'serializer':serializer})

    def post(self, request):
        # Reference
        # https://www.django-rest-framework.org/tutorial/3-class-based-views/
        # http://www.chenxm.cc/article/244.html
        # http://webdocs.cs.ualberta.ca/~hindle1/2014/07-REST.pdf
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
    # Reference
    # https://segmentfault.com/a/1190000010970988
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
