# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.urls import reverse_lazy
from django.views import generic

from .models import *

from django.contrib.auth.models import User

from .serializers import *

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

from django.core.paginator import Paginator

DEBUG = False

# Reference: Django class-based view
# https://docs.djangoproject.com/en/2.1/topics/class-based-views/


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# External API Views
#
# These are the views that are used for the REST API
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Posts(APIView):
    """
    get:
    get all public posts from server
    """
    def get(self, request):
        resp = {}

        posts = Post.objects.filter(visibility = "PUBLIC").all().order_by('-published')

        count = len(posts)
        resp['count'] = count

        pageSize = request.GET.get('size')
        if not pageSize:
            pageSize = 50

        pageSize = int(pageSize)

        resp['size'] = pageSize

        paginator = Paginator(posts,pageSize)
        posts = paginator.get_page(request.GET.get('page'))


        next = None;
        previous = None;

        if posts.has_next():
            resp['next'] = str(request.get_host())+"/posts?page="+str(posts.next_page_number())
        if posts.has_previous():
            resp['previous'] = str(request.get_host())+"/posts?page="+str(posts.previous_page_number())

        serializer = PostSerializer(posts, many=True)
        
        # paginate comments
        for post in serializer.data:
            post['size'] = pageSize
            comments = Comment.objects.filter(post_id=post['id']).all()
            commentPaginator = Paginator(comments, pageSize)
            comments = commentPaginator.get_page(0)
            post['comments'] = GETCommentSerializer(comments, many=True).data

        resp['posts'] = serializer.data

        resp['query'] = 'posts'

        return Response(resp)

class PostById(APIView):
    """
    get:
    get a post by it's {post_id}
    """
    def get(self, request, post_id):
        posts = Post.objects.filter(post_id=post_id).first()
        serializer = PostSerializer(posts)
        return Response(
            {
                "query": "getPost",
                "post" : serializer.data,
                }
            )

class AuthorPosts(APIView):
    """
    get:
    get all posts visible to current authenticated user

    post:
    Create a post for the currently authenticated user
    """
    def get(self, request):
        resp = {}

        user = UserProfile.objects.filter(user_id=request.user).first()
        posts = Post.objects.filter(visibility = "PUBLIC").all()
        posts = posts | Post.objects.filter(user_id=user).exclude(visibility="PUBLIC").all()

        # TODO add friend stuff to this, will just do non-friend for now

        # TODO add post_visible_to stuff

        count = len(posts)
        resp['count'] = count

        pageSize = request.GET.get('size')
        if not pageSize:
            pageSize = 50

        pageSize = int(pageSize)

        resp['size'] = pageSize

        paginator = Paginator(posts,pageSize)
        posts = paginator.get_page(request.GET.get('page'))


        next = None;
        previous = None;

        if posts.has_next():
            resp['next'] = str(request.get_host())+"/posts?page="+str(posts.next_page_number())
        if posts.has_previous():
            resp['previous'] = str(request.get_host())+"/posts?page="+str(posts.previous_page_number())

        serializer = PostSerializer(posts, many=True)
        
        # paginate comments
        for post in serializer.data:
            post['size'] = pageSize
            comments = Comment.objects.filter(post_id=post['id']).all()
            commentPaginator = Paginator(comments, pageSize)
            comments = commentPaginator.get_page(0)
            post['comments'] = GETCommentSerializer(comments, many=True).data

        resp['posts'] = serializer.data

        resp['query'] = 'posts'

        return Response(resp)

    def post(self, request):
        # TODO implement post creation by API Call
        return Response({ "data": "none", "success": True }, status=status.HTTP_200_OK)

class AuthorPostsById(APIView):
    """
    get:
    get all posts made by {author_id} and visible to current user
    """
    def get(self, request, author_id):
        resp = {}

        request_user = UserProfile.objects.filter(user_id=request.user).first()
        author = UserProfile.objects.filter(author_id=author_id).first()
        print(UserProfile.objects.first().author_id)
        posts = Post.objects.filter(user_id = author).filter(visibility="PUBLIC").all()

        # TODO add friend stuff to this

        # TODO implement visible_to

        count = len(posts)
        resp['count'] = count

        pageSize = request.GET.get('size')
        if not pageSize:
            pageSize = 50

        pageSize = int(pageSize)

        resp['size'] = pageSize

        paginator = Paginator(posts,pageSize)
        posts = paginator.get_page(request.GET.get('page'))


        next = None;
        previous = None;

        if posts.has_next():
            resp['next'] = str(request.get_host())+"/posts?page="+str(posts.next_page_number())
        if posts.has_previous():
            resp['previous'] = str(request.get_host())+"/posts?page="+str(posts.previous_page_number())

        serializer = PostSerializer(posts, many=True)
        
        # paginate comments
        for post in serializer.data:
            post['size'] = pageSize
            comments = Comment.objects.filter(post_id=post['id']).all()
            commentPaginator = Paginator(comments, pageSize)
            comments = commentPaginator.get_page(0)
            post['comments'] = GETCommentSerializer(comments, many=True).data

        resp['posts'] = serializer.data

        resp['query'] = 'posts'

        return Response(resp)
        
class CommentsByPostId(APIView):
    """
    get:
    get comments given a {post_id}

    post:
    create new comment on {post_id}
    """
    def get(self, request, post_id):
        resp = {}
        
        comments = Comment.objects.filter(post_id=post_id).all()

        count = len(comments)
        resp['count'] = count

        pageSize = request.GET.get('size')
        if not pageSize:
            pageSize = 50

        pageSize = int(pageSize)

        resp['size'] = pageSize

        paginator = Paginator(comments,pageSize)
        comments = paginator.get_page(request.GET.get('page'))


        next = None;
        previous = None;

        if comments.has_next():
            resp['next'] = str(request.get_host())+"/posts?page="+str(comments.next_page_number())
        if comments.has_previous():
            resp['previous'] = str(request.get_host())+"/posts?page="+str(comments.previous_page_number())

        serializer = GETCommentSerializer(comments, many=True)
        
        resp['comments'] = serializer.data

        resp['query'] = 'comments'

        return Response(resp)

    def post(self, request, post_id):
        return Response({ "data": "none", "success": True }, status=status.HTTP_200_OK)

class FriendListByAuthorId(APIView):
    """
    get:
    get friend list of {author_id}

    post:
    Ask if anyone in provided list is a friend of {author_id} 
    """
    def get(self, request, author_id):
        return Response({ "data": "none", "success": True }, status=status.HTTP_200_OK)

    def post(self, request, author_id):
        return Response({ "data": "none", "success": True }, status=status.HTTP_200_OK)

class CheckFriendStatus(APIView):
    """
    get:
    check if {author1_id} and {author2_id} are friends
    """
    def get(self, request, author1_id, author2_id):
        return Response({ "data": "none", "success": True }, status=status.HTTP_200_OK)

class FriendRequest(APIView):
    """
    post:
    Make a friend request
    """
    def post(self, request):
        # follow = Follow.objects.create()
        return Response({ "data": "none", "success": True }, status=status.HTTP_200_OK)

class AuthorProfile(APIView):
    """
    get:
    get an author's profile
    """
    def get(self, request, author_id):
        return Response({ "data": "none", "success": True }, status=status.HTTP_200_OK)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Internal API Views
#
# These are the views that are used for the frontend
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
        friends.append(GETProfileSerializer(f).data)
    context = {'flist': friends, 'userprofile':user}
    return render(request,'friends.html', context)

class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

    def form_valid(self, form):
        form_object = form.save(commit=False)
        form_object.is_active = False
        form_object.save()
        uu = User.objects.filter(id=form_object.id).first()
        UserProfile.objects.create(user_id=uu, displayName=uu.username, host=str(self.request.get_host()))
        return super(SignUp, self).form_valid(form)

class UserViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = GETProfileSerializer

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

    def get(self, request, author_id):
        profileContent = dict()
        #print(UserProfile.objects.filter(author_id = author_id).first())
        profileContent['displayName'] = UserProfile.objects.filter(author_id = author_id).first().displayName
        profileContent['author_id'] = UserProfile.objects.filter(author_id = author_id).first().author_id
        profileContent['bio'] = UserProfile.objects.filter(author_id = author_id).first().bio
        profileContent['host'] = UserProfile.objects.filter(author_id = author_id).first().host
        profileContent['github'] = UserProfile.objects.filter(author_id = author_id).first().github
        profileContent['url'] = UserProfile.objects.filter(author_id = author_id).first().url
        serializer_profile = GETProfileSerializer(profileContent)
        response = {"query":"profile", "profile":serializer_profile.data}
        return Response(response)

    """
    get:
    Get the profile for a given {author_id}
    """
'''
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
'''

def GetAuthorProfile(request, author_id):
    user = UserProfile.objects.filter(author_id=author_id).first()
    requestuser = UserProfile.objects.filter(user_id=request.user).first()
    content = dict()
    content["UserProfile"] = user # this is the requested user profile
    # please do not change it.. I know it is kinda confusing
    content["userprofile"] = requestuser # this is the request user profile
    return render(request, 'profile.html', content)


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
    def get(self, request, post_id):
        comments = Comment.objects.filter(post_id = post_id).order_by("published").all()
        pageSize = request.GET.get('size')
        commentSize = len(comments)
        if not pageSize:
            pageSize = 50
        paginator = Paginator(comments,pageSize)
        comments = paginator.get_page(request.GET.get('page'))
        commentSerializer = GETCommentSerializer(comments, many=True)
        response = {"query":"comments", "count":commentSize, "comments":commentSerializer.data,"size":pageSize}
        if comments.has_next():
            response["next"] = str(request.get_host())+"/posts/"+str(post_id)+"/comments?page="+str(comments.next_page_number())
        if comments.has_previous():
            response["previous"] = str(request.get_host())+"/posts/"+str(post_id)+"/comments?page="+str(comments.previous_page_number())
        return Response(response)
    '''
    def post(self, request, post_id):
        form = CreateComment(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('/#'+str(post_id))
        return redirect('/')
    '''


    def post(self, request, post_id):
        #data = request.data
        #print(data)

        comment_data = dict()
        #comment_data['query'] == 'addcomment'
        post = Post.objects.filter(post_id=post_id)
        comment_data['user_id'] = request.data['comment']['author']['id'].split('/')[-1]
        comment_data['content'] = request.data['comment']['comment']
        comment_data['post_id'] = post_id #request.data['psot'].split(...)
        comment_data['contentType'] = request.data['comment']['contentType']

        print(comment_data)
        failed = False

        comment_serializer = CommentSerializer(data=comment_data)

        if comment_serializer.is_valid():
            comment_serializer.save()
        else:
            failed = True
        if not failed:
            return Response({"success": True, "message": "Comment Saved"}, status=status.HTTP_200_OK)
        else:
            return Response({"success": True, "message": "Comment Error"}, status=status.HTTP_400_BAD_REQUEST)




class AuthorPostsOld(APIView):
    """
    get:
    Get all posts visible to current user
    post:
    Create a new post as current user
    """
    def get(self, request):
        """
        here we need to return all the posts that are visible for the current user
        This will work even if the request user is unknown or does not exist in our server
        """
        postList = []
        # request user
        user = UserProfile.objects.filter(user_id=request.user).first()
        # PUBLIC post
        #(This will return for the remote server request)
        public_post = Post.objects.filter(visibility="PUBLIC").all()
        postList += list(public_post)
        # users own post
        #(This will not return since we don't have inforamtion about remote user's post information)
        own_post = Post.objects.filter(user_id=user.author_id).exclude(visibility="PUBLIC").all()
        postList += list(own_post)
        # see friends post  (private to friends)
        #(This will return for the remote server request since there could be remote server user friends with our server user)
        friends_userprofile = find_friends(user) # get a list of friends userprofile object
        for friend in friends_userprofile:
            # get all the friends private post
            friendPrivatePosts = Post.objects.filter(visibility="FRIENDS", user_id=friend).all()
            postList += list(friendPrivatePosts)
        # see friends post's that is visible to me (private to certain users, and I am one of them who can see it)
        #(This will return for the remote server request)
        all_visible_post_object = PostVisibleTo.objects.filter(user_id=user.author_id).all()
        for i in all_visible_post_object:
            post = Post.objects.filter(post_id=i.post_id.post_id).first()
            postList += list(post)

        # TODO
        # ask remotely to other servers for visible posts (must avoid duplicate posts)
        # firend of friends (must avoid duplicate posts)


        # sort all the post according to the publish time
        # https://stackoverflow.com/questions/403421/how-to-sort-a-list-of-objects-based-on-an-attribute-of-the-objects
        # author: Triptych https://stackoverflow.com/users/43089/triptych
        postList.sort(key=lambda post: post.published, reverse=True)
        postSize = len(postList)
        #
        pageSize = request.GET.get('size')
        if not pageSize:
            pageSize = 50
        paginator = Paginator(postList,pageSize)
        postList = paginator.get_page(request.GET.get('page'))
        # make the return JSON in the consistent format (also include all the post information including: comments,authors)
        serializer_post = GETPostSerializer(postList, many=True)
        response = {"query":"posts", "count":postSize, "posts":serializer_post.data, "size":pageSize}
        if postList.has_next():
            response["next"] = str(request.get_host())+"/author/posts?page="+str(postList.next_page_number())
        if postList.has_previous():
            response["previous"] = str(request.get_host())+"/author/posts?page="+str(postList.previous_page_number())

        return Response(response)


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


class MakePost(APIView):
    """
    get:
    Render a making post html page to current user
    """
    renderer_classes = [TemplateHTMLRenderer]
    #model = Post
    template_name = '../templates/post.html'
    #fields = ['title', 'description','content', 'content-options', 'isibility-select']
    #login_url="/accounts/login/"

    def get(self, request):
        #print(request.body)
        posts = Post.objects.all()
        serializer = PostSerializer()
        return Response({'serializer':serializer})


def profile(request):
    # user has login
    userprofile = UserProfile.objects.filter(user_id = request.user.id).first()
    args = {'userprofile':userprofile} # pass in the whole user object
    return render(request, 'profile.html',args)

def edit_profile(request):
    # user has login
    if request.method == "POST":
        # POST
        userprofile = UserProfile.objects.filter(user_id = request.user).first()
        form = EditProfileForm(request.POST, instance=userprofile)
        if form.is_valid():
            form.save()
            # text = form.cleaned_data['displayName']
            return redirect('/accounts/profile/'+str(userprofile.author_id)+'/')
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
