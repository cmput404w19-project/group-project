from django.test import TestCase
from django.test import Client
from rest_framework.test import APIRequestFactory
from django.test.client import RequestFactory 
from rest_framework.test import force_authenticate
from accounts.models import *
from accounts.views import * 
from django.contrib.auth.models import User
import uuid
import json
import socket

#this test is reference answered by Pedro M Duarte from https://stackoverflow.com/questions/2619102/djangos-self-client-login-does-not-work-in-unit-tests
# create superuser answered by Sam Dolan from https://stackoverflow.com/questions/3495114/how-to-create-admin-user-in-django-tests-py

def createUser(username1, password1):

    user = User.objects.create_superuser(username1, "nobody@gmail.com", password1)
    user.is_active = True
    user.save()
    return user

def setupUser(user,display_name):
    
    newuser = UserProfile()
    uuid1 = uuid.uuid4()
    newuser.author_id = uuid1
    newuser.user_id = user
    newuser.displayName = display_name
    newuser.bio = "bio"
    newuser.host = "http://127.0.0.1:8000/"
    newuser.github = "https://github.com/cmput404w19-project/"
    newuser.url = "http://127.0.0.1:8000/author/" + str(uuid1)
    newuser.save()
    return newuser

def createPost(user):
    post1 = Post()
    post1.typeChoice = ('text/markdown', 'text/markdown')
    post1.visibilityChoice = ("PUBLIC","PUBLIC")
    post1.post_id = uuid.uuid4()
    post1.user_id = user
    post1.title = "This is title"
    post1.description = "This is description"
    post1.source = "myself"
    post1.origin = "myself"
    post1.content = "This is content"
    post1.category = "category"
    post1.visibility = "PUBLIC"
    post1.unlisted = False
    post1.save()
    return post1

def createComment(user, post):
    comment = Comment()
    comment.typeChoice = ('text/markdown', 'text/markdown')
    comment.comment_id = uuid.uuid4()
    comment.user_id = user.url
    comment.contentType = "text/plain"
    comment.post_id = post
    comment.save()
    return comment

def createFriendObject(url1, url2):
    follow1 = Follow()
    follow2 = Follow()
    follow1.follower_url = url1
    follow1.following_url = url2
    follow2.follower_url = url2
    follow2.following_url = url1
    follow1.save()
    follow2.save()

def createFollow(url1, url2):
    follow1 = Follow()
    follow1.follower_url = url1
    follow1.following_url = url2
    follow1.save()

def createFriendRequest(user1, user2):

    request = FriendRequest()
    request.statusChoice = ("Pending","Pending")
    request.requestedBy_name = user2.displayName
    request.requestedBy_url = user2.url
    request.requestedTo_url = user1.url
    request.save()

class PostTest(TestCase):

    def setUp(self):
        global temp_user1
        self.user1 = createUser("kehan1", "1")
        temp_user1 = setupUser(self.user1, "user1")
        self.post1 = createPost(temp_user1)
        self.factory = RequestFactory()
    
    def test_post(self):
        view = Posts.as_view()
        c = Client()
        login = c.login(username='kehan1',password='1')
        self.assertTrue(login)
        self.assertEqual(temp_user1.displayName, "user1")
        request = self.factory.get("http://127.0.0.1:8000/posts/")
        force_authenticate(request, user=self.user1)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        post = response.data["posts"][0]
        post_id = post['id']
        self.assertEqual(post_id, self.post1.post_id)
        

class PostByIdTest(TestCase):

    def setUp(self):
        global temp_user1
        self.user1 = createUser("kehan1", "1")
        temp_user1 = setupUser(self.user1, "user1")
        # self.user2 = createUser("kehan2", "2")
        # temp_user2 = setupUser(self.user2, "user2")
        self.post1 = createPost(temp_user1)
        self.factory = RequestFactory()
    
    def test_postbyid(self):
        view = PostById.as_view()
        c = Client()
        login = c.login(username='kehan1',password='1')
        self.assertTrue(login)
        self.assertEqual(temp_user1.displayName, "user1")
        request = self.factory.get("http://127.0.0.1:8000/posts/"+str(self.post1.post_id))
        force_authenticate(request, user=self.user1)
        response = view(request, self.post1.post_id)
        self.assertTrue(response.status_code, 200)
        post = response.data["post"]
        post_id = post['id']
        self.assertEqual(post_id, self.post1.post_id)

class AuthorPostsByIdTest(TestCase):
    
    def setUp(self):
        global temp_user1, temp_user2

        self.user1 = createUser("kehan1", "1")
        temp_user1 = setupUser(self.user1, "user1")
        self.user2 = createUser("kehan2", "2")
        temp_user2 = setupUser(self.user2, "user2")

        self.post1 = createPost(temp_user1)
        self.post2 = createPost(temp_user2)

        self.factory = RequestFactory()

    def test_authorpostbyid(self):
        view = AuthorPostsById.as_view()
        c = Client()
        login = c.login(username='kehan1', password='1')
        self.assertTrue(login)
        self.assertEqual(temp_user1.displayName, "user1")
        author_id = str(temp_user2.author_id)
        #reference from https://www.django-rest-framework.org/api-guide/testing/
        request = self.factory.get("http://127.0.0.1:8000/author/"+ author_id +"/posts/")
        force_authenticate(request, user=self.user1)
        response = view(request, temp_user2.author_id)
        self.assertEqual(response.status_code, 200)
        post = response.data["posts"][0]
        post_id = post.get("id")
        self.assertEqual(post_id, self.post2.post_id)


class CommentsByPostIdTest(TestCase):

    def setUp(self):
        global temp_user1, temp_user2

        self.user1 = createUser("kehan1", "1")
        temp_user1 = setupUser(self.user1, "user1")
        self.user2 = createUser("kehan2", "2")
        temp_user2 = setupUser(self.user2, "user2")

        self.post1 = createPost(temp_user1)
        self.comment = createComment(temp_user2, self.post1)

        self.factory = RequestFactory()
    
    def test_commentbypostid(self):
        view = CommentsByPostId.as_view()
        c = Client()
        login = c.login(username='kehan1', password='1')
        self.assertTrue(login)
        post_id = str(self.post1.post_id)
        request1 = self.factory.get("http://127.0.0.1:8000/posts/"+ post_id +"/comments/")
        
        data = {
        "query": "addComment",
        "comment":{
            "author":{
            "host": temp_user1.host,
            "displayName": temp_user1.displayName,
            "url": temp_user1.url,
            "github": temp_user1.github},
        "comment": "this is a test comment",
        "contentType":"text/plain"
        }}
        data1 = json.dumps(data)
        request2 = self.factory.post("http://127.0.0.1:8000/posts/"+ post_id +"/comments/", data1, content_type='application/json')
        force_authenticate(request2, user=self.user1)
        response = view(request2, self.post1.post_id)
        self.assertEqual(response.status_code, 200)


class FriendListByAuthorIdTest(TestCase):

    def setUp(self):
        global temp_user1, temp_user2

        self.user1 = createUser("kehan1", "1")
        temp_user1 = setupUser(self.user1, "user1")
        self.user2 = createUser("kehan2", "2")
        temp_user2 = setupUser(self.user2, "user2")
        createFriendObject(temp_user1.url, temp_user2.url)
        self.factory = RequestFactory()

    def test_getfriend(self):
        view = FriendListByAuthorId.as_view()
        c = Client()
        login = c.login(username='kehan1', password='1')
        self.assertTrue(login)
        ###not finish since cannot set http header for getting meta data


class FriendRequestNewTest(TestCase):

    def setUp(self):
        global temp_user1, temp_user2

        self.user1 = createUser("kehan1", "1")
        temp_user1 = setupUser(self.user1, "user1")
        self.user2 = createUser("kehan2", "2")
        temp_user2 = setupUser(self.user2, "user2")
        #createFriendRequest(temp_user1, temp_user2)
        self.factory = RequestFactory()
    
    def test_friendRequest(self):
        view = FriendRequestNew.as_view()
        c = Client()
        login = c.login(username='kehan1', password='1')
        self.assertTrue(login)
        
        data = {
              "author": {
                "id": temp_user2.url,
                "host": temp_user2.host,
                "displayName": temp_user2.displayName,
                "url": temp_user2.url
              },
              "friend": {
                "id": temp_user1.url,
                "host": temp_user1.host,
                "displayName": temp_user1.displayName,
                "url": temp_user1.url
              }
            }
        data1 = json.dumps(data)
        request = self.factory.post("http://127.0.0.1:8000/friendrequest/", data1, content_type='application/json')
        force_authenticate(request, user=self.user2)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        send_status = response.data["success"]
        self.assertTrue(send_status)


class acceptFriendRequestTest(TestCase):

    def setUp(self):
        global temp_user1, temp_user2

        self.user1 = createUser("kehan1", "1")
        temp_user1 = setupUser(self.user1, "user1")
        self.user2 = createUser("kehan2", "2")
        temp_user2 = setupUser(self.user2, "user2")
        createFriendRequest(temp_user1, temp_user2)
        self.factory = RequestFactory()

    def test_acceptrequest(self):
        view = acceptFriendRequest.as_view()
        c = Client()
        login = c.login(username='kehan1', password='1')
        self.assertTrue(login)

        data = {
                "query": "deleteFriendrequest",
                "author":{
                  "url": temp_user1.url,
                },
                "friend": {
                  "url": temp_user2.url,
                }
              }

        data1 = json.dumps(data)
        request = self.factory.post("http://127.0.0.1:8000/acceptfriendrequest/", data1, content_type='application/json')
        force_authenticate(request, user=self.user1)
        response = view(request)
        self.assertEqual(response.status_code, 200)
    
class deleteFriendRequestTest(TestCase):

    def setUp(self):
        global temp_user1, temp_user2

        self.user1 = createUser("kehan1", "1")
        temp_user1 = setupUser(self.user1, "user1")
        self.user2 = createUser("kehan2", "2")
        temp_user2 = setupUser(self.user2, "user2")
        createFriendRequest(temp_user1, temp_user2)
        self.factory = RequestFactory()
    
    def test_deleteFriendRequest(self):

        view = deleteFriendRequest.as_view()
        c = Client()
        login = c.login(username='kehan1', password='1')
        self.assertTrue(login)

        data = {
                "query": "deleteFriendrequest",
                "author":{
                  "id": temp_user1.url,
                },
                "friend": {
                  "id":temp_user2.url,
                }
              }
        data1 = json.dumps(data)
        request = self.factory.post("http://127.0.0.1:8000/deletefriendrequest/", data1, content_type='application/json')
        force_authenticate(request, user=self.user1)
        response = view(request)
        self.assertEqual(response.status_code, 200)

    
class AuthorProfileTest(TestCase):

    def setUp(self):
        global temp_user1
        self.user1 = createUser("kehan1", "1")
        temp_user1 = setupUser(self.user1, "user1")
        self.factory = RequestFactory()
    
    def test_authorprofile(self):

        view = AuthorProfile.as_view()
        c = Client()
        login = c.login(username='kehan1', password='1')
        self.assertTrue(login)
        request = self.factory.get("http://127.0.0.1:8000/author/" + str(temp_user2.author_id)+"/")
        force_authenticate(request, user=self.user1)
        response = view(request, temp_user1.author_id)
        self.assertEqual(response.status_code, 200)
        author_id = response.data['id'].split('/')[-1]
        self.assertEqual(author_id, str(temp_user1.author_id))

class ExternalServerTest(TestCase):

    def setUp(self):
        global temp_user1
        self.user1 = createUser("kehan1", "1")
        temp_user1 = setupUser(self.user1, "user1")
        self.factory = RequestFactory()
    
    def test_authorprofile(self):

        view = ExternalEndpoints.as_view()
        c = Client()
        login = c.login(username='kehan1', password='1')
        self.assertTrue(login)
        request = self.factory.get("http://127.0.0.1:8000/externalendpoints/")
        force_authenticate(request, user=self.user1)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data)


class UnFollowTest(TestCase):

    def setUp(self):

        global temp_user1, temp_user2
        self.user1 = createUser("kehan1", "1")
        temp_user1 = setupUser(self.user1, "user1")
        self.user2 = createUser("kehan2", "2")
        temp_user2 = setupUser(self.user2, "user2")
        createFollow(temp_user1.url, temp_user2.url)
        self.factory = RequestFactory()

    def test_unfollow(self):

        view = UnFollow.as_view()
        c = Client()
        login = c.login(username='kehan1', password='1')
        self.assertTrue(login)

        data = {
              "author": {
                "id": temp_user1.url,
                "host": temp_user1.host,
                "displayName": temp_user1.displayName,
                "url": temp_user1.url
              },
              "friend": {
                "id": temp_user2.url,
                "host": temp_user2.host,
                "displayName": temp_user2.displayName,
                "url": temp_user2.url
              }
            }
        data1 = json.dumps(data)
        request = self.factory.post("http://127.0.0.1:8000/unfollowrequest/",data1, content_type='application/json')
        force_authenticate(request, user=self.user1)
        response = view(request)
        self.assertEqual(response.status_code, 200)
 
class postDeleteTest(TestCase):

    def setUp(self):

        global temp_user1
        self.user1 = createUser("kehan1", "1")
        temp_user1 = setupUser(self.user1, "user1")
        self.post1 = createPost(temp_user1)
        self.factory = RequestFactory()

    def test_postDelete(self):

        view = postDelete.as_view()
        c = Client()
        login = c.login(username='kehan1', password='1')
        self.assertTrue(login)

        request = self.factory.post("http://127.0.0.1:8000/post/delete/"+str(self.post1.post_id))
        force_authenticate(request, user=self.user1)
        response = view(request, self.post1.post_id)
        self.assertEqual(response.status_code, 302)


class PublicPostsTest(TestCase):

    def setUp(self):

        self.user1 = createUser("kehan1", "1")
        temp_user1 = setupUser(self.user1, "kehan1")
        self.post1 = createPost(temp_user1)
        self.factory = RequestFactory()

    def test_publicposts(self):
        
        view = MakePost.as_view()
        c = Client()
        login = c.login(username='kehan1', password='1')
        self.assertTrue(login)

        request = self.factory.get("http://127.0.0.1:8000/author/render/post")
        force_authenticate(request, user=self.user1)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        post_user = response.data["userprofile"]
        self.assertEqual(post_user.displayName, self.user1.username)



    
