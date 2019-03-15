from django.test import TestCase
from accounts.models import *
from django.contrib.auth.models import User
import uuid

# the reference of this model test is from https://docs.djangoproject.com/en/2.1/topics/testing/overview/

class UserProfileTestCase(TestCase):
    
    def setUp(self):
        global thisId
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

    def test_Userprofile(self):
        kehan_name = UserProfile.objects.get(author_id=thisId)
        self.assertEqual(kehan_name.displayName, "kehan1")
    
class PostTestCase(TestCase):
    
    def setUp(self):
        global thisId
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
    
    def test_Post(self):
        post = Post.objects.get(user_id=thisId)
        self.assertEqual(post.description, "This is description")

class CommentTestCase(TestCase):

    def setUp(self):
        global thisId
        global commentId
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

        comment = Comment()
        comment.typeChoice = ('text/plain','text/plain')
        commentId = uuid.uuid4()
        comment.comment_id = commentId
        comment.user_id = kehan1
        comment.content = "my comment"
        comment.contentType = "text/plain"
        comment.post_id = post1
        comment.save()

    def test_comment(self):
        comment = Comment.objects.get(comment_id=commentId)
        self.assertEqual(comment.user_id.author_id, thisId)

class FollowTestCase(TestCase):

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

        follow = Follow()
        follow.follower_id = kehan1
        print(follow.follower_id)
        follow.following_id = kehan2
        follow.save()

    def test_follow(self):
        follow = Follow.objects.get(follower_id=kehan1, following_id=kehan2)
        self.assertTrue(follow)


class RequestTestCase(TestCase):
    
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

        request = FriendRequest()
        request.statusChoice = ("Pending","Pending")
        request.requestedBy_id = kehan1
        request.requestedTo_id = kehan2
        request.request_status = "Pending"
        request.save()

    def test_request(self):
        request = FriendRequest.objects.get(requestedBy_id=kehan1, requestedTo_id=kehan2)
        self.assertEqual(request.request_status, "Pending")
