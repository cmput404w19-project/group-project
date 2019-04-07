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
    newuser.github = "https://github.com/cmput404w19-project/group-project/projects"
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


class PostTest(TestCase):

    def setUp(self):
        global temp_user1
        self.user1 = createUser("kehan1", "1")
        temp_user1 = setupUser(self.user1, "user1")
        self.post1 = createPost(temp_user1)
    
    def test_post(self):
        c = Client()
        login = c.login(username='kehan1',password='1')
        self.assertTrue(login)
        self.assertEqual(temp_user1.displayName, "user1")
        response = self.client.get("http://127.0.0.1:8000/posts/")
        self.assertTrue(response.status_code, 200)
        post = response.data["posts"][0]
        post_id = post.get("id")
        self.assertEqual(post_id, self.post1.post_id)

class PostByIdTest(TestCase):

    def setUp(self):
        global temp_user1
        self.user1 = createUser("kehan1", "1")
        temp_user1 = setupUser(self.user1, "user1")
        # self.user2 = createUser("kehan2", "2")
        # temp_user2 = setupUser(self.user2, "user2")
        self.post1 = createPost(temp_user1)
    
    def test_postbyid(self):
        c = Client()
        login = c.login(username='kehan1',password='1')
        self.assertTrue(login)
        self.assertEqual(temp_user1.displayName, "user1")
        response = self.client.get("http://127.0.0.1:8000/posts/"+str(self.post1.post_id))
        self.assertTrue(response.status_code, 200)
        post = response.data["post"]
        post_id = post.get("id")
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

# class FriendRequestTest(TestCase):

#     def setUp(self):
#         global kehan1
#         global kehan2
#         self.user = User.objects.create(username = 'kehan_wang')
#         self.user.set_password('Mypossword123')
#         self.user.is_active = True
#         self.user.save()

#         thisId = uuid.uuid4()
#         kehan1 = UserProfile()
#         thisId = uuid.uuid4()
#         kehan1.author_id=thisId 
#         # kehan1.user_id = User.objects.create_user(username='kehan_wang', email="kehan1@ualberta.ca",password="Mypossword123", is_active=True)
#         kehan1.user_id = self.user
#         kehan1.displayName="kehan1"
#         kehan1.bio="bio"
#         kehan1.host="host"
#         kehan1.github="https://github.com/cmput404w19-project/group-project/projects",
#         kehan1.url="https://github.com/cmput404w19-project/group-project/projects"
#         kehan1.save()

#         thisId2 = uuid.uuid4()
#         kehan2 = UserProfile()
#         thisId2 = uuid.uuid4()
#         kehan2.author_id=thisId 
#         kehan2.user_id = User.objects.create_user(username='kehan_wang2', email="kehan1@ualberta.ca",password="Mypossword123", is_active=True)
#         kehan2.displayName="kehan2"
#         kehan2.bio="bio2"
#         kehan2.host="host2"
#         kehan2.github="https://github.com/cmput404w19-project/group-project/projects2",
#         kehan2.url="https://github.com/cmput404w19-project/group-project/projects2"
#         kehan2.save()


#     def test_bad_friendRequest(self):
#         c = Client()
#         login = c.login(username='kehan_wang',password='Mypossword123')
#         self.assertTrue(login)
#         request = self.client.post('friendrequest/', {},  format='application/json')
#         self.assertEqual(request.status_code, 404)






# class HomeTest(TestCase):

#     def setUp(self):
#         self.user = User.objects.create_superuser(username = 'kehan_wang')
#         self.user.set_password('Mypossword123')
#         self.user.is_active = True
#         self.user.save()
#         global kehan1  
#         thisId = uuid.uuid4()
#         kehan1 = UserProfile()
#         thisId = uuid.uuid4()
#         kehan1.author_id=thisId 
#         kehan1.user_id = self.user
#         kehan1.displayName="kehan1"
#         kehan1.bio="bio"
#         kehan1.host="host"
#         kehan1.github="https://github.com/cmput404w19-project/group-project/projects",
#         kehan1.url="https://github.com/cmput404w19-project/group-project/projects"
#         kehan1.save()

#     def test_home(self):

#         c = Client()
#         login = c.login(username='kehan_wang',password='Mypossword123')
#         self.assertTrue(login)
#         request = self.client.get('http://127.0.0.1:8000/')
#         self.assertEqual(request.status_code, 200)
    

# # class AuthorProfileTest(TestCase):
# #     def setUp(self):
# #         self.user = User.objects.create(username = 'kehan_wang')
# #         self.user.set_password('Mypossword123')
# #         self.user.is_active = True
# #         self.user.save()
# #         global kehan1  
# #         thisId = uuid.uuid4()
# #         kehan1 = UserProfile()
# #         thisId = uuid.uuid4()
# #         kehan1.author_id=thisId 
# #         kehan1.user_id = self.user
# #         kehan1.displayName="kehan1"
# #         kehan1.bio="bio"
# #         kehan1.host="host"
# #         kehan1.github="https://github.com/cmput404w19-project/group-project/projects",
# #         kehan1.url="https://github.com/cmput404w19-project/group-project/projects"
# #         kehan1.save()

# #     def test_authorProfile(self):

# #         c = Client()
# #         login = c.login(username='kehan_wang',password='Mypossword123')
# #         self.assertTrue(login)
# #         request = self.client.get('http://127.0.0.1:8000/accounts/profile/')
# #         self.assertEqual(request.status_code, 302)
# #         request = self.client.get('http://127.0.0.1:8000/posts/')
# #         self.assertEqual(request.status_code, 200)

# class PostTest(TestCase):

#     def setUp(self):
#         self.user = User.objects.create(username = 'kehan_wang')
#         self.user.set_password('Mypossword123')
#         self.user.is_active = True
#         self.user.save()
#         global kehan1  
#         thisId = uuid.uuid4()
#         kehan1 = UserProfile()
#         thisId = uuid.uuid4()
#         kehan1.author_id=thisId 
#         kehan1.user_id = self.user
#         kehan1.displayName="kehan1"
#         kehan1.bio="bio"
#         kehan1.host="host"
#         kehan1.github="https://github.com/cmput404w19-project/group-project/projects",
#         kehan1.url="https://github.com/cmput404w19-project/group-project/projects"
#         kehan1.save()

#         post1 = Post()
#         post1.typeChoice = ('text/markdown', 'text/markdown')
#         post1.visibilityChoice = ("PUBLIC","PUBLIC")
#         post1.post_id = thisId
#         post1.user_id = kehan1
#         post1.description = "This is description"
#         post1.source = "myself"
#         post1.origin = "myself"
#         post1.content = "This is content"
#         post1.category = "category"
#         post1.visibility = "PUBLIC"
#         post1.unlisted = True
#         post1.save()
#         self.post1 = post1

#         comment = Comment()
#         comment.typeChoice = ('text/plain','text/plain')
#         commentId = uuid.uuid4()
#         comment.comment_id = commentId
#         comment.user_id = kehan1
#         comment.content = "my comment"
#         comment.contentType = "text/plain"
#         comment.post_id = post1
#         comment.save()
#         self.comment = comment

#     def test_postandcomment(self):
#         c = Client()
#         login = c.login(username='kehan_wang',password='Mypossword123')
#         self.assertTrue(login)
#         #get post
#         request = self.client.get('http://127.0.0.1:8000/posts/%s' %(self.post1.post_id))
#         self.assertTrue(request.status_code, 200)

#         #get comment
#         request = self.client.get('http://127.0.0.1:8000/posts/%s/comment' %(self.post1.post_id))
#         self.assertTrue(request.status_code, 200)


# # class AuthorPostsTest(TestCase):

# #     def setUp(self):
# #         self.user = User.objects.create(username='kehan_wang')
# #         self.user.set_password('Mypossword123')
# #         self.user.is_active = True
# #         self.user.save()

# #         global kehan1
# #         thisId = uuid.uuid4()
# #         kehan1 = UserProfile()
# #         thisId = uuid.uuid4()
# #         kehan1.author_id=thisId 
# #         kehan1.user_id = self.user
# #         kehan1.displayName="kehan1"
# #         kehan1.bio="bio"
# #         kehan1.host="host"
# #         kehan1.github="https://github.com/cmput404w19-project/group-project/projects",
# #         kehan1.url="https://github.com/cmput404w19-project/group-project/projects"
# #         kehan1.save()
    
# #     def test_authorpost(self):
# #         c = Client()
# #         login = c.login(username='kehan_wang',password='Mypossword123')
# #         self.assertTrue(login)
# #         request = self.client.get('http://127.0.0.1:8000/author/posts/')
        
# #         self.assertEqual(request.status_code, 200)



# class unFollowTest(TestCase):

#     def setUp(self):
#         self.user = User.objects.create(username='kehan_wang')
#         self.user.set_password('Mypossword123')
#         self.user.is_active = True
#         self.user.save()

#         global kehan1
#         global kehan2
#         thisId = uuid.uuid4()
#         kehan1 = UserProfile()
#         thisId = uuid.uuid4()
#         kehan1.author_id=thisId 
#         kehan1.user_id = self.user
#         kehan1.displayName="kehan1"
#         kehan1.bio="bio"
#         kehan1.host="host"
#         kehan1.github="https://github.com/cmput404w19-project/group-project/projects",
#         kehan1.url="https://github.com/cmput404w19-project/group-project/projects"
#         kehan1.save()

#         thisId2 = uuid.uuid4()
#         kehan2 = UserProfile()
#         thisId2 = uuid.uuid4()
#         kehan2.author_id=thisId 
#         kehan2.user_id = User.objects.create_user(username='kehan_wang2', email="kehan1@ualberta.ca",password="Mypossword123", is_active= True)
#         kehan2.displayName="kehan2"
#         kehan2.bio="bio2"
#         kehan2.host="host2"
#         kehan2.github="https://github.com/cmput404w19-project/group-project/projects2",
#         kehan2.url="https://github.com/cmput404w19-project/group-project/projects2"
#         kehan2.save()

#         follow = Follow()
#         follow.follower_id = kehan1
#         follow.following_id = kehan2
#         follow.save()

    
#     def test_unfollow(self):
#         c = Client()
#         login = c.login(username='kehan_wang',password='Mypossword123')
#         self.assertTrue(login)
#         follow_id = Follow.objects.filter(follower_id = kehan1.author_id, following_id = kehan2.author_id).first()
#         self.assertTrue(follow_id)
#         request = self.client.post("http://127.0.0.1:8000/unfollowrequest/%d/" %(follow_id.pk))
#         self.assertTrue(request.status_code, 200)
