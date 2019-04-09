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

from django.http import HttpResponseNotFound, HttpResponseBadRequest, HttpResponse

from django.core.paginator import Paginator

from urllib import request
import urllib
import requests, urllib

from django.http import HttpResponse
import base64

DEBUG = False

# Reference: Django class-based view
# https://docs.djangoproject.com/en/2.1/topics/class-based-views/


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# External API Views
#
# These are the views that are used for the REST API
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# given author_url return list of all friends
def find_friends(author_url):
    following = Follow.objects.filter(following_url=author_url).all()
    following_list = FollowSerializer(following, many=True)
    following_url_list = list(following_list.data[i]['follower_url'] for i in range(len(following_list.data)))

    followers = Follow.objects.filter(follower_url=author_url).all()
    follower_list = FollowSerializer(followers, many=True)
    follower_url_list = list(follower_list.data[i]['following_url'] for i in range(len(follower_list.data)))

    # initialize the list of friends with all our local friends
    friend_list = list(set(following_url_list) & set(follower_url_list))

    # our list of remaining people to check
    remaining_follows_to_check = list(set(follower_url_list) - set(friend_list))

    # for all non-local friends, we need to check with other servers to see if the follow relation
    # exists on their end

    author1_id = author_url.split('/')[-1]
    for follow in remaining_follows_to_check:
        author2_host  = '/'.join(follow.split('/')[0:3])
        author2_url = urllib.parse.quote_plus(follow)
        r = requests.get("{}/author/{}/friends/{}".format(author2_host,author1_id, author2_url))
        if r.status_code != 200:
            continue
        data = r.json()
        if data['friends']:
            friend_list.append(follow)

    return friend_list

class Posts(APIView):
    """
    get:
    get all public posts from server
    """
    def get(self, request):
        if request.user.is_authenticated:
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
            # No need to return next if last page
            # No need to return previous if page is 0
            # next = None;
            # previous = None;
            if posts.has_next():
                resp['next'] =  str(request.scheme)+"://"+str(request.get_host())+"/posts?page="+str(posts.next_page_number())
            if posts.has_previous():
                resp['previous'] = str(request.scheme)+"://"+str(request.get_host())+"/posts?page="+str(posts.previous_page_number())
            serializer = PostSerializer(posts, many=True)
            # paginate comments
            for post in serializer.data:
                post['size'] = pageSize
                comments = Comment.objects.filter(post_id=post['id']).order_by("-published").all()
                commentPaginator = Paginator(comments, pageSize)
                post['next'] = str(request.scheme)+"://"+str(request.get_host())+"/posts/"+str(post['id'])+"/comments"
                post['origin'] = str(request.scheme)+"://"+str(request.get_host())+"/posts/"+str(post['id'])
                post['source'] = str(request.scheme)+"://"+str(request.get_host())+"/posts/"+str(post['id'])
                comments = commentPaginator.get_page(0)
                comments = GETCommentSerializer(comments, many=True).data
                post['comments'] = comments
            resp['posts'] = serializer.data
            resp['query'] = 'posts'
            return Response(resp)

        else:
            # unauthorized
            return HttpResponse('Unauthorized', status=401)

class PostById(APIView):
    """
    get:
    get a post by it's {post_id}
    """
    def get(self, request, post_id):
        if request.user.is_authenticated:
            resp = {'query': 'getPost'}
            posts = Post.objects.filter(post_id=post_id).first()
            serializer = PostSerializer(posts)
            pageSize = request.GET.get('size')
            if not pageSize:
                pageSize = 50
            pageSize = int(pageSize)
            post = serializer.data
            post['size'] = pageSize
            comments = Comment.objects.filter(post_id=post['id']).order_by("-published").all()
            commentPaginator = Paginator(comments, pageSize)
            comments = commentPaginator.get_page(0)
            comments = GETCommentSerializer(comments, many=True).data
            post['comments'] = comments
            resp['post'] = post
            return Response(resp)
        else:
            # unauthorized
            return HttpResponse('Unauthorized', status=401)


class AuthorPosts(APIView):
    """
    get:
    get all posts visible to current authenticated user

    post:
    Create a post for the currently authenticated user

    Important: in order to return "friend" and "private" and "serveronly" posts 
    the one who sen d the request MUST have this header:
    X-request-user-ID
    """
    def get(self, request):
        resp = {}
        # look for the userprofile if this is our own server user
        if request.user.is_authenticated:
            user = UserProfile.objects.filter(user_id=request.user).first()
        else:
            return HttpResponse('Unauthorized', status=401)
        # All the public posts
        posts = Post.objects.filter(visibility = "PUBLIC").all()
        posts = list(posts)
        # Only for our own server user
        if request.user.is_authenticated:
            # user's own post and prevent duplication
            # by excluding those are public
            if user:
                # if this user's userprofile exists in our server 
                # that means this is our own server user 
                # not external endpoint user
                posts += list(Post.objects.filter(user_id=user.author_id).exclude(visibility="PUBLIC").all())
        # return all friends post which the authors are following this requested user
        thisRequestUserUrl = request.META.get('HTTP_X_REQUEST_USER_ID') # this is the CUSTOM header we shared within connected group
        print("URL IS FROM :",request.META)
        print(thisRequestUserUrl)
        if thisRequestUserUrl:
            # get all visibility = "FRIENDS"
            all_user_who_follow_requestUser = Follow.objects.filter(following_url=thisRequestUserUrl).all().values_list('follower_url', flat=True)
            # add all request user 's follower
            for userurl in all_user_who_follow_requestUser:
                authorid = userurl.rstrip("/").split("/")[-1]  # this was url so need to extract author id
                # find this user's "friend"(follower) post
                posts += list(Post.objects.filter(visibility="FRIENDS").filter(user_id=authorid).all())
                # here also check for request user is in our server
                if user:
                    # if the followers of the request user on our server has SERVERONLY
                    # and this request user is our server user 
                    # get all the "SERVERONLY" post for this user
                    posts += list(Post.objects.filter(visibility="SERVERONLY").filter(user_id=authorid).all())
        # TODO add post_visible_to stuff
        # Get all visibility as "PRIVATE"
        if thisRequestUserUrl:
            all_private_posts = Post.objects.filter(visibility="PRIVATE").all()
            for private_post in all_private_posts:
                # check the visibleTo table
                all_who_can_see = PostVisibleTo.objects.filter(post_id=private_post.post_id).values_list('user_url', flat=True)
                if thisRequestUserUrl in all_who_can_see:
                    # if this user is indeed inside the visibleTo list
                    posts.append(private_post)
        count = len(posts)
        resp['count'] = count
        pageSize = request.GET.get('size')
        if not pageSize:
            pageSize = 50
        pageSize = int(pageSize)
        resp['size'] = pageSize
        # posts = list(posts)
        posts.sort(key=lambda post: post.published, reverse=True)
        paginator = Paginator(posts,pageSize)
        posts = paginator.get_page(request.GET.get('page'))
        # No need to return next if last page
        # No need to return previous if page is 0
        # next = None;
        # previous = None;
        if posts.has_next():
            resp['next'] = str(request.scheme)+"://"+str(request.get_host())+"/author/posts?page="+str(posts.next_page_number())
            if pageSize != 50:
                resp['next'] += "&size="+str(pageSize)
        if posts.has_previous():
            resp['previous'] = str(request.scheme)+"://"+str(request.get_host())+"/author/posts?page="+str(posts.previous_page_number())
            if pageSize != 50:
                resp['previous'] += "&size="+str(pageSize)
        serializer = PostSerializer(posts, many=True)
        # paginate comments and add friend list
        #counter = 0
        for post in serializer.data:
            #counter += 1
            post['size'] = pageSize
            #print(counter)
            #print(comments)
            comments = Comment.objects.filter(post_id=post['id']).order_by("-published").all()
            commentPaginator = Paginator(comments, pageSize)
            comments = commentPaginator.get_page(0)
            post['next'] = str(request.scheme)+"://"+str(request.get_host())+"/posts/"+str(post['id'])+"/comments"
            post['origin'] = str(request.scheme)+"://"+str(request.get_host())+"/posts/"+str(post['id'])
            post['source'] = str(request.scheme)+"://"+str(request.get_host())+"/posts/"+str(post['id'])
            comments = GETCommentSerializer(comments, many=True).data
            post['comments'] = comments

        resp['posts'] = serializer.data
        resp['query'] = 'posts'
        return Response(resp)

    def post(self, request):
        # TODO implement post creation by API Call
        # Reference
        # https://www.django-rest-framework.org/tutorial/3-class-based-views/
        # http://www.chenxm.cc/article/244.html
        # http://webdocs.cs.ualberta.ca/~hindle1/2014/07-REST.pdf
        #profile = get_object_or_404(Profile, pk=pk)
        if request.user.is_authenticated:
            new_data = request.data.copy()
            user_id = str(UserProfile.objects.filter(user_id = request.user).first().author_id)
            new_data.__setitem__("user_id", user_id)
            host = request.scheme + "://" + request.get_host() +  "/"
            new_data["host"] = host
            serializer = PostSerializer(data=new_data)
            if not serializer.is_valid():
                return Response({'serializer': serializer})
            serializer.save()
            # TODO Response cannot allow a redirect so just use redirect('/') now
            return redirect('/')
        else:
            return HttpResponse('Unauthorized', status=401)

class AuthorPostsById(APIView):
    """
    get:
    get all posts made by {author_id} and visible to current user
    """
    def get(self, request, author_id):
        if not request.user.is_authenticated:
            return HttpResponse('Unauthorized', status=401)
        resp = {}
        # public posts that is made by this author
        author = UserProfile.objects.filter(author_id=author_id).first()
        posts = Post.objects.filter(user_id = author).filter(visibility="PUBLIC").all()
        posts = list(posts)
        request_user = UserProfile.objects.filter(user_id=request.user).first()
        print("------")
        print(request_user.author_id)
        print(author_id)
        print("------")
        if request_user:
            if str(request_user.author_id) == str(author_id):
                print("check")
                posts += list(Post.objects.filter(user_id = author).exclude(visibility="PUBLIC").all())
        # TODO add friend stuff to this
        thisRequestUserUrl = request.META.get('HTTP_X_REQUEST_USER_ID') # this is the CUSTOM header we shared within connected group
        print(thisRequestUserUrl)
        if thisRequestUserUrl:
            # get all visibility = "FRIENDS"
            all_user_who_follow_requestUser = Follow.objects.filter(following_url=thisRequestUserUrl).all().values_list('follower_url', flat=True)
            # add all request user 's follower
            for userurl in all_user_who_follow_requestUser:
                authorid = userurl.rstrip("/").split("/")[-1]  # this was url so need to extract author id
                if authorid == str(author_id):
                    # find this user's "friend"(follower) post
                    posts += list(Post.objects.filter(visibility="FRIENDS").filter(user_id=authorid).all())
                    break
        else:
            all_user_who_follow_requestUser = Follow.objects.filter(following_url=request_user.url).all().values_list('follower_url', flat=True)
            # add all request user 's follower
            for userurl in all_user_who_follow_requestUser:
                authorid = userurl.rstrip("/").split("/")[-1]  # this was url so need to extract author id
                if authorid == str(author_id):
                    # find this user's "friend"(follower) post
                    posts += list(Post.objects.filter(visibility="FRIENDS").filter(user_id=authorid).all())
                    break

        # TODO implement visible_to

        count = len(posts)
        resp['count'] = count
        pageSize = request.GET.get('size')
        if not pageSize:
            pageSize = 50
        pageSize = int(pageSize)
        resp['size'] = pageSize
        posts.sort(key=lambda post: post.published, reverse=True)
        paginator = Paginator(posts,pageSize)
        posts = paginator.get_page(request.GET.get('page'))
        # No need to return next if last page
        # No need to return previous if page is 0
        # next = None;
        # previous = None;
        if posts.has_next():
            resp['next'] = str(request.scheme)+"://"+str(request.get_host())+"/author/"+str(author_id)+"/posts?page="+str(posts.next_page_number())
        if posts.has_previous():
            resp['previous'] = str(request.scheme)+"://"+str(request.get_host())+"/author/"+str(author_id)+"/posts?page="+str(posts.previous_page_number())
        serializer = PostSerializer(posts, many=True)
         # paginate comments and add friend list
        for post in serializer.data:
            post['size'] = pageSize
            comments = Comment.objects.filter(post_id=post['id']).order_by("-published").all()
            commentPaginator = Paginator(comments, pageSize)
            comments = commentPaginator.get_page(0)
            post['next'] = str(request.scheme)+"://"+str(request.get_host())+"/posts/"+str(post['id'])+"/comments"
            post['origin'] = str(request.scheme)+"://"+str(request.get_host())+"/posts/"+str(post['id'])
            post['source'] = str(request.scheme)+"://"+str(request.get_host())+"/posts/"+str(post['id'])
            comments = GETCommentSerializer(comments, many=True).data
            post['comments'] = comments
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
        if not request.user.is_authenticated:
            return HttpResponse('Unauthorized', status=401)
        resp = {}
        comments = Comment.objects.filter(post_id=post_id).order_by("-published").all()
        count = len(comments)
        resp['count'] = count
        pageSize = request.GET.get('size')
        if not pageSize:
            pageSize = 50
        pageSize = int(pageSize)
        resp['size'] = pageSize
        paginator = Paginator(comments,pageSize)
        comments = paginator.get_page(request.GET.get('page'))
        if comments.has_next():
            resp['next'] = str(request.scheme)+"://"+str(request.get_host())+"/posts/"+str(post_id)+"/comments?page="+str(comments.next_page_number())
        if comments.has_previous():
            resp['previous'] = str(request.scheme)+"://"+str(request.get_host())+"/posts/"+str(post_id)+"/comments?page="+str(comments.previous_page_number())
        serializer = GETCommentSerializer(comments, many=True)
        resp['comments'] = serializer.data
        resp['query'] = 'comments'
        return Response(resp)

    def post(self, request, post_id):
        if not request.user.is_authenticated:
            return HttpResponse('Unauthorized', status=401)
        #data = request.data
        comment_data = dict()
        #comment_data['query'] == 'addcomment'
        #post = Post.objects.filter(post_id=post_id)
        user_url = request.data['comment']['author']['url']
        comment_data['user_id'] = user_url
        comment_data['content'] = request.data['comment']['comment']
        comment_data['post_id'] = post_id #request.data['post'].split(...)
        comment_data['contentType'] = request.data['comment']['contentType']
        failed = False
        print(comment_data)
        comment_serializer = CommentSerializer(data=comment_data)
        if comment_serializer.is_valid():
            comment_serializer.save()
        else:
            failed = True
        if not failed:
            return Response({"success": True, "message": "Comment Saved"}, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Comment Error"}, status=status.HTTP_400_BAD_REQUEST)
        #return Response({ "data": "none", "success": True }, status=status.HTTP_200_OK)



class FriendListByAuthorId(APIView):
    """
    get:
    get friend list of {author_id}

    post:
    Ask if anyone in provided list is a friend of {author_id}
    """
    def get(self, request, author_id):
        resp = {}

        protocol = str(self.request.scheme)
        author_url = "{}://{}/author/{}".format(protocol, request.META["HTTP_HOST"], author_id)

        resp['authors'] = find_friends(author_url)

        resp['query'] = 'friends'

        return Response(resp)

    def post(self, request, author_id):
        resp = {}

        protocol = str(self.request.scheme)
        author_url = "{}://{}/author/{}".format(protocol, request.META["HTTP_HOST"], author_id)

        if request.data['author'] != author_url:
            return Response({"success": False, "message": "bad query", "query":"friends"}, status=status.HTTP_400_BAD_REQUEST)

        resp["query"] = "friends"

        resp["author"] = author_url

        friend_list = []

        friends_of_author = find_friends(author_url)

        for author in request.data['authors']:
            if author in friends_of_author:
                friend_list.append(author)

        resp["authors"] = friend_list

        return Response(resp)

class CheckFriendStatus(APIView):
    """
    get:
    check if {author1_id} follows {author2_id}
    """

    def get(self, request, author1_id, author2_id):
        resp = {}

        # We just check for a follow relation from author_1 to author_2, since that's all we really care about here

        # build the URL of the first user so we can check
        protocol = str(self.request.scheme)
        author_url = "{}://{}/author/{}".format(protocol, request.META["HTTP_HOST"], author1_id)

        author2_url = urllib.parse.unquote_plus(author2_id)
        follows = Follow.objects.filter(follower_url=author_url, following_url=author2_url).all()

        if len(follows) == 0:
            resp['friends'] = False
        else:
            resp['friends'] = True

        resp['query'] = 'friends'

        resp['authors'] = [author_url, author2_url]

        return Response(resp)

class FriendRequestNew(APIView):
    """
    post:
    Make a friend request
    """
    def post(self, request):

        data2 = {}
        data2['requestedBy_name'] = request.data['author']['displayName']
        data2['requestedBy_url'] = request.data['author']['url']
        data2['requestedTo_url'] = request.data['friend']['url']
        data2['request_status'] = "Pending"

        try:
            FriendRequest.objects.get(requestedBy_url=data2['requestedBy_url'], requestedTo_url=data2['requestedTo_url'])
            return Response(status=status.HTTP_200_OK)
        except:
            friend_request_serializer = FriendRequestSerializer(data=data2)

        if friend_request_serializer.is_valid():
            friend_request_serializer.save()
        else:
            return Response(friend_request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({ "query": "friendrequest", "success": True, "message": "Friend request sent" }, status=status.HTTP_200_OK)

class InternalFriendRequest(APIView):

    def post(self, request):
        data = {}
        data['follower_url'] = request.data['author']['url']
        data['following_url'] = request.data['friend']['url']
        follow_serializer = FollowSerializer(data=data)
        send_do_domain_name = str(data['following_url'])
        send_do_domain_name = send_do_domain_name.split('author')[0]
        url = send_do_domain_name + 'friendrequest/'

        csrf_token = request.META['CSRF_COOKIE']
        if follow_serializer.is_valid():
            follow_serializer.save()
            headers = {'content-type': 'application/json', 'X-CSRFToken':csrf_token}
            data = json.dumps(request.data)
            r = requests.post(url, data= data, headers=headers)

        else:
            return Response(follow_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({ "query": "friendrequest", "success": True, "message": "Friend request sent" }, status=status.HTTP_200_OK)


class acceptFriendRequest(APIView):
    """
    post:
    Make a friend request
    """
    def post(self, request):
        data = {}
        data['follower_url'] = request.data['author']['url']
        data['following_url'] = request.data['friend']['url']
        follow_serializer = FollowSerializer(data=data)

        if follow_serializer.is_valid():
            follow_serializer.save()
        else:
            return Response(follow_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if 'weeb-tears' in request.data['friend']['url']:
            friend_profile_request = requests.get(request.data['friend']['url'])
            friend_profile = friend_profile_request.json()
            author_profile_request = requests.get(request.data['author']['url'])
            author_profile = author_profile_request.json()

            new_payload = {}
            new_payload['friend'] = {}
            new_payload['author'] = {}

            new_payload['query'] = 'friendrequest'
            new_payload['friend']['id'] = friend_profile['id']
            new_payload['friend']['displayName'] = friend_profile['displayName']
            new_payload['friend']['host'] = friend_profile['host']
            new_payload['friend']['url'] = friend_profile['url']

            new_payload['query'] = 'profilerequest'
            new_payload['author']['id'] = author_profile['id']
            new_payload['author']['displayName'] = author_profile['displayName']
            new_payload['author']['host'] = author_profile['host']
            new_payload['author']['url'] = author_profile['url']

            new_payload['query'] = "friendrequest"

            resp = requests.post("https://weeb-tears.herokuapp.com/friendrequest", auth=HTTPBasicAuth("Team14-Prod-User", "qweqweqweqwe"), data=new_payload)

        print("follow serialzer pass")
        return Response({ "query": "friendrequest", "success": True, "message": "Friend request sent" }, status=status.HTTP_200_OK)



class deleteFriendRequest(APIView):
     def post(self, request):

        requestedTo_url = request.data['author']['id']
        requestedBy_url = request.data['friend']['id']
        obj = FriendRequest.objects.get(requestedBy_url=requestedBy_url, requestedTo_url=requestedTo_url)
        obj.delete()
        return Response(status=status.HTTP_200_OK)





class AuthorProfile(APIView):
    """
    get:
    get an author's profile
    """
    def get(self, request, author_id):
        profile = UserProfile.objects.filter(author_id=author_id).first()
        resp = GETProfileSerializer(profile).data

        # resp['friends'] = find_friends(resp['id'])

        return Response(resp)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Internal API Views
#
# These are the views that are used for the frontend
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ExternalEndpoints(APIView):
    """
    get:
    get all external endpoints
    """
    def get(self, request):
        endpoints = ExternalServer.objects.all()
        serializer = ExternalServerSerializer(endpoints, many=True)
        return Response(serializer.data)


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
        protocol = str(request.scheme)+"://"
        user = UserProfile.objects.filter(user_id=request.user).first()
        if user.url == "":
            user.url = protocol+str(request.get_host())+"/author/"+str(user.author_id)
            user.save()
        if user.host == "":
            user.host = protocol+str(request.get_host())
            user.save()
        context["userprofile"] = user
        # get all the follow list of this user (a list of people that this user are following)
        followinglist = Follow.objects.filter(follower_url=user.url).all().values_list('following_url', flat=True)
        context["followlist"] = " ".join(followinglist)
        # since this is our server, no need domain name for the url just the path
        # so this will be our post api path
        endpoints = ExternalServer.objects.all()
        endpoints_url_list = []
        for i in endpoints:
            endpoints_url_list.append(i.server_url)
        context["endpoints_url_string"] = " ".join(endpoints_url_list)
        context["author_post_api_url"] = protocol+str(request.get_host())  # this path url should handle to get all posts that is visible for this user
        return render(request, 'home.html', context)
    else:
        # not login
        return render(request, 'landingPage.html')

def friendlistpage(request):
    userprofile = UserProfile.objects.filter(user_id=request.user).first()
    # find all friends of this current users
    list_of_friend_urls = find_friends(userprofile.url)
    list_of_friend_urls = " ".join(list_of_friend_urls)
    context = {"list_of_friend_urls":list_of_friend_urls}
    context["userprofile"] = userprofile
    return render(request, 'friends.html', context)


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

    def form_valid(self, form):
        protocol = str(self.request.scheme)+"://"
        form_object = form.save(commit=False)
        form_object.is_active = False
        form_object.save()
        uu = User.objects.filter(id=form_object.id).first()
        UserProfile.objects.create(user_id=uu, displayName=uu.username, host=protocol + str(self.request.get_host()))
        user_profile = UserProfile.objects.filter(user_id=uu).first()
        user_profile.url = user_profile.host + '/author/' + str(user_profile.author_id)
        user_profile.save()
        return super(SignUp, self).form_valid(form)

class UserViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = GETProfileSerializer

class UnFollow(APIView):
    """
    post:
    make an unfollow request
    of the form
    {
        follower_url: url
        following_url: url
    }
    """
    def post(self, request):

        follower_url = request.data['author']['id']
        following_url = request.data['friend']['id']
        obj = Follow.objects.get(follower_url=follower_url, following_url=following_url)
        obj.delete()
        return Response(status=status.HTTP_200_OK)

class FriendRequestOld(APIView):
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
        return Response({ "query": "friendrequest", "success": True, "message": "Friend request sent"}, status=status.HTTP_200_OK)
        #return render(request,'friend_requests.html', context)

def GetAuthorProfile(request):
    # user = UserProfile.objects.filter(author_id=author_id).first()
    requestuser = UserProfile.objects.filter(user_id=request.user).first()
    content = dict()
    # content["UserProfile"] = user # this is the requested user profile
    content["userprofile"] = requestuser # this is the request user's profile
    # get the request parameter
    profile_url = request.GET.get("profile_url")
    if not profile_url:
        HttpResponseBadRequest("bad request! No profile url in the request body")
    # send a request to api to ask for the userprofile data
    # try:
    #     with request.urlopen(profile_url) as f:
    #         encode = f.headers.get_content_charset()
    #         if not encode:
    #             encode = 'utf-8'
    #         data = f.read().decode(encode)
    #         data = json.loads(data)
    #         content["RequestforthisUserProfile"] = data
    # except:
    #     return HttpResponseBadRequest("bad request! No profile url in the request body")
    content["profile_url"] = profile_url
    follow = Follow.objects.filter(follower_url=requestuser.url, following_url=profile_url)
    if not follow:
        content["followExists"] = 'false'
    else:
        content["followExists"] = 'true'

    return render(request, 'profile.html', content)

def getFriendRequest(request):
    #user = UserProfile.objects.filter(author_id=request.user).first()
    content = dict()
    content["User"] = request.user
    requestuser = UserProfile.objects.filter(user_id=request.user).first()
    #reference answered by akotian https://stackoverflow.com/questions/14639106/how-can-i-retrieve-a-list-of-field-for-all-objects-in-django
    follower = FriendRequest.objects.filter(requestedTo_url=requestuser.url).all()#.values_list('requestedBy_url', flat=True)
    content["follower"] = follower
    content["userprofile"] = requestuser


    return render(request, 'friend_requests.html', content)



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

class UpdateGithubId(APIView):

    def post(self, request):
        user = request.user
        newId = request.data['id']
        print(newId)

        user = User.objects.get(id=user.id)
        user.githubLastId = newId
        user.save()

        return HttpResponse(status=status.HTTP_204_NO_CONTENT)

class GitHubView(APIView):
    def get(self, request):
        user = request.user
        data = GETProfileSerializer(user).data
        github = data['github']
        github_id = github.split('/')[-1]
        return render(request, 'edit_profile.html', context={'user': data})
    #def post(self, request):
    def post(self, request):

        user = request.user
        request_serializer = GETProfileSerializer(user)
        update = (request.POST).dict()
        for attribute, value in update.items():
            if value != "":
                setattr(user, attribute, value)
        try:
            user.save()
        except:
            github_url = request_serializer.data['github']
            github_username = github_url.split('/')[-1]
            return render(request, 'edit_profile.html', \
                context={'user': request_serializer.data, 'github_username':github_username,
                'error_message':'Error'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = GETProfileSerializer(user)
        github_url = serializer.data['github']
        github_username = github_url.split('/')[-1]
        return HttpResponseRedirect(reverse('frontauthorposts', args=[user.id]))



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
        user = UserProfile.objects.filter(user_id=request.user).first()
        posts = Post.objects.filter(user_id=user.author_id).all()
        postDic = {}
        #print("--------")
        for post in posts:
            if (post.contentType == 'image/png;base64' or post.contentType == 'image/jpeg;base64'):
                postDic[str(post.title)] = str(post.host) + "posts/" + str(post.post_id) + "/render/image"
        #print(postDic)
        serializer = PostSerializer()

        userprofile = UserProfile.objects.filter(user_id = request.user).first()
        friendlist = find_friends(userprofile.url)
        friendlist = " ".join(friendlist)
        context = {}
        context["serializer"] = serializer
        context["friendlist"] = friendlist
        context["postDic"] = postDic
        context["userprofile"] = userprofile
        return Response(context)

def ShowMyPosts(request, author_id):
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
        protocol = str(request.scheme)+"://"
        user = UserProfile.objects.filter(user_id=request.user).first()
        if user.url == "":
            user.url = protocol+str(request.get_host())+"/author/"+str(user.author_id)
            user.save()
        if user.host == "":
            user.host = protocol+str(request.get_host())
            user.save()
        context["userprofile"] = user
        # get all the follow list of this user (a list of people that this user are following)
        followinglist = Follow.objects.filter(follower_url=user.url).all().values_list('following_url', flat=True)
        context["followlist"] = " ".join(followinglist)
        # since this is our server, no need domain name for the url just the path
        # so this will be our post api path
        endpoints = ExternalServer.objects.all()
        endpoints_url_list = []
        for i in endpoints:
            endpoints_url_list.append(i.server_url)
        context["endpoints_url_string"] = " ".join(endpoints_url_list)
        context["author_post_api_url"] = protocol+str(request.get_host())  # this path url should handle to get all posts that is visible for this user
        return render(request, 'MyPosts.html', context)
    else:
        # not login
        return render(request, 'landingPage.html')

def RenderPostByID(request, post_id):
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
        protocol = str(request.scheme)+"://"
        user = UserProfile.objects.filter(user_id=request.user).first()
        if user.url == "":
            user.url = protocol+str(request.get_host())+"/author/"+str(user.author_id)
            user.save()
        if user.host == "":
            user.host = protocol+str(request.get_host())
            user.save()
        context["userprofile"] = user
        # get all the follow list of this user (a list of people that this user are following)
        followinglist = Follow.objects.filter(follower_url=user.url).all().values_list('following_url', flat=True)
        context["followlist"] = " ".join(followinglist)
        # since this is our server, no need domain name for the url just the path
        # so this will be our post api path
        endpoints = ExternalServer.objects.all()
        endpoints_url_list = []
        for i in endpoints:
            endpoints_url_list.append(i.server_url)
        context["endpoints_url_string"] = " ".join(endpoints_url_list)
        context["author_post_api_url"] = protocol+str(request.get_host())  # this path url should handle to get all posts that is visible for this user
        context["post_id"] = post_id
        return render(request, 'RenderPostByID.html', context)
    else:
        # not login
        return render(request, 'landingPage.html')


# Reference:
# Antti Haapala Jul 26 '14 at 14:00
# https://stackoverflow.com/questions/24971729/django-python-todataurl-return-a-response-with-the-string-from-todataurl
def RenderPostByIDImage(request, post_id):
    post = Post.objects.filter(post_id = post_id).first()
    #print(post.content)
    image_data = post.content.partition('base64,')[2]
    return HttpResponse(
        base64.b64decode(image_data), content_type='image/jpg'
    )


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
            return redirect('/accounts/profile/?profile_url='+userprofile.url)
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
