from django.test import TestCase
from django.test import Client
from rest_framework.test import APIRequestFactory
from accounts.models import *
from django.contrib.auth.models import User
import uuid
import json

#this test is reference from https://stackoverflow.com/questions/2619102/djangos-self-client-login-does-not-work-in-unit-tests

class FriendRequestTest(TestCase):

    def setUp(self):
        global kehan1
        global kehan2
        thisId = uuid.uuid4()
        kehan1 = UserProfile()
        thisId = uuid.uuid4()
        kehan1.author_id=thisId 
        kehan1.user_id = User.objects.create_user(username='kehan_wang', email="kehan1@ualberta.ca",password="Mypossword123")
        kehan1.displayName="kehan1"
        kehan1.bio="bio"
        kehan1.host="host"
        kehan1.github="https://github.com/cmput404w19-project/group-project/projects",
        kehan1.url="https://github.com/cmput404w19-project/group-project/projects"
        kehan1.save()

        thisId2 = uuid.uuid4()
        kehan2 = UserProfile()
        thisId2 = uuid.uuid4()
        kehan2.author_id=thisId 
        kehan2.user_id = User.objects.create_user(username='kehan_wang2', email="kehan1@ualberta.ca",password="Mypossword123")
        kehan2.displayName="kehan2"
        kehan2.bio="bio2"
        kehan2.host="host2"
        kehan2.github="https://github.com/cmput404w19-project/group-project/projects2",
        kehan2.url="https://github.com/cmput404w19-project/group-project/projects2"
        kehan2.save()

        

    def test_bad_friendRequest(self):
        c = Client()
        login = c.login(username='kehan_wang',password='Mypossword123')
        self.assertTrue(login)
        request = self.client.post('friendrequest/', {},  format='application/json')
        self.assertEqual(request.status_code, 404)





class HomeTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username = 'kehan_wang')
        self.user.set_password('Mypossword123')
        self.user.save()
        global kehan1  
        thisId = uuid.uuid4()
        kehan1 = UserProfile()
        thisId = uuid.uuid4()
        kehan1.author_id=thisId 
        kehan1.user_id = self.user
        kehan1.displayName="kehan1"
        kehan1.bio="bio"
        kehan1.host="host"
        kehan1.github="https://github.com/cmput404w19-project/group-project/projects",
        kehan1.url="https://github.com/cmput404w19-project/group-project/projects"
        kehan1.save()

    def test_home(self):

        c = Client()
        login = c.login(username='kehan_wang',password='Mypossword123')
        self.assertTrue(login)
        request = self.client.get('http://127.0.0.1:8000/')
        self.assertEqual(request.status_code, 200)
    

class AuthorProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username = 'kehan_wang')
        self.user.set_password('Mypossword123')
        self.user.save()
        global kehan1  
        thisId = uuid.uuid4()
        kehan1 = UserProfile()
        thisId = uuid.uuid4()
        kehan1.author_id=thisId 
        kehan1.user_id = self.user
        kehan1.displayName="kehan1"
        kehan1.bio="bio"
        kehan1.host="host"
        kehan1.github="https://github.com/cmput404w19-project/group-project/projects",
        kehan1.url="https://github.com/cmput404w19-project/group-project/projects"
        kehan1.save()

    def test_authorProfile(self):

        c = Client()
        login = c.login(username='kehan_wang',password='Mypossword123')
        self.assertTrue(login)
        request = self.client.get('http://127.0.0.1:8000/accounts/profile/')
        self.assertEqual(request.status_code, 302)
        request = self.client.get('http://127.0.0.1:8000/posts/')
        self.assertEqual(request.status_code, 200)

class PostTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username = 'kehan_wang')
        self.user.set_password('Mypossword123')
        self.user.save()
        global kehan1  
        thisId = uuid.uuid4()
        kehan1 = UserProfile()
        thisId = uuid.uuid4()
        kehan1.author_id=thisId 
        kehan1.user_id = self.user
        kehan1.displayName="kehan1"
        kehan1.bio="bio"
        kehan1.host="host"
        kehan1.github="https://github.com/cmput404w19-project/group-project/projects",
        kehan1.url="https://github.com/cmput404w19-project/group-project/projects"
        kehan1.save()

        post1 = Post()
        post1.typeChoice = ('text/markdown', 'text/markdown')
        post1.visibilityChoice = ("PUBLIC","PUBLIC")
        post1.post_id = thisId
        post1.user_id = kehan1
        post1.description = "This is description"
        post1.source = "myself"
        post1.origin = "myself"
        post1.content = "This is content"
        post1.category = "category"
        post1.visibility = "PUBLIC"
        post1.unlisted = True
        post1.save()
        self.post1 = post1

        comment = Comment()
        comment.typeChoice = ('text/plain','text/plain')
        commentId = uuid.uuid4()
        comment.comment_id = commentId
        comment.user_id = kehan1
        comment.content = "my comment"
        comment.contentType = "text/plain"
        comment.post_id = post1
        comment.save()
        self.comment = comment

    def test_postandcomment(self):
        c = Client()
        login = c.login(username='kehan_wang',password='Mypossword123')
        self.assertTrue(login)
        #get post
        request = self.client.get('http://127.0.0.1:8000/posts/%s' %(self.post1.post_id))
        self.assertTrue(request.status_code, 200)

        #get comment
        request = self.client.get('http://127.0.0.1:8000/posts/%s/comment' %(self.post1.post_id))
        self.assertTrue(request.status_code, 200)


class AuthorPostsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='kehan_wang')
        self.user.set_password('Mypossword123')
        self.user.save()

        global kehan1
        thisId = uuid.uuid4()
        kehan1 = UserProfile()
        thisId = uuid.uuid4()
        kehan1.author_id=thisId 
        kehan1.user_id = self.user
        kehan1.displayName="kehan1"
        kehan1.bio="bio"
        kehan1.host="host"
        kehan1.github="https://github.com/cmput404w19-project/group-project/projects",
        kehan1.url="https://github.com/cmput404w19-project/group-project/projects"
        kehan1.save()
    
    def test_authorpost(self):
        c = Client()
        login = c.login(username='kehan_wang',password='Mypossword123')
        self.assertTrue(login)
        request = self.client.get('http://127.0.0.1:8000/author/posts/')
        
        self.assertEqual(request.status_code, 200)



class unFollowTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='kehan_wang')
        self.user.set_password('Mypossword123')
        self.user.save()

        global kehan1
        global kehan2
        thisId = uuid.uuid4()
        kehan1 = UserProfile()
        thisId = uuid.uuid4()
        kehan1.author_id=thisId 
        kehan1.user_id = self.user
        kehan1.displayName="kehan1"
        kehan1.bio="bio"
        kehan1.host="host"
        kehan1.github="https://github.com/cmput404w19-project/group-project/projects",
        kehan1.url="https://github.com/cmput404w19-project/group-project/projects"
        kehan1.save()

        thisId2 = uuid.uuid4()
        kehan2 = UserProfile()
        thisId2 = uuid.uuid4()
        kehan2.author_id=thisId 
        kehan2.user_id = User.objects.create_user(username='kehan_wang2', email="kehan1@ualberta.ca",password="Mypossword123")
        kehan2.displayName="kehan2"
        kehan2.bio="bio2"
        kehan2.host="host2"
        kehan2.github="https://github.com/cmput404w19-project/group-project/projects2",
        kehan2.url="https://github.com/cmput404w19-project/group-project/projects2"
        kehan2.save()

        follow = Follow()
        follow.follower_id = kehan1
        follow.following_id = kehan2
        follow.save()

    
    def test_unfollow(self):
        c = Client()
        login = c.login(username='kehan_wang',password='Mypossword123')
        self.assertTrue(login)
        follow_id = Follow.objects.filter(follower_id = kehan1.author_id, following_id = kehan2.author_id).first()
        self.assertTrue(follow_id)
        request = self.client.post("http://127.0.0.1:8000/unfollowrequest/%d/" %(follow_id.pk))
        self.assertTrue(request.status_code, 200)
