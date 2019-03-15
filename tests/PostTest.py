from django.test import TestCase
from accounts.models import *
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class PostTestCase(TestCase):

    def setUp(self):
        global user_id, post_id
        user_id = uuid.uuid4()
        chengze = UserProfile()
        chengze.author_id = user_id
        chengze.user_id = User.objects.create_user(username='kehan_wang', email="kehan1@ualberta.ca",password="Mypossword123")
        chengze.displayName="chengze"
        chengze.bio="bio"
        chengze.host="https://localhost/"
        chengze.github="https://github.com/chengze2",
        chengze.url="https://github.com/cmput404w19-project/group-project.git"
        chengze.save()

        post_id1 = uuid.uuid4()
        post1 = Post()
        post1.post_id = post_id
        post1.user_id = chengze
        post1.title = "Test Title 1"
        post1.description = "Test Description 1"
        post1.source = ""
        post1.origin = ""
        post1.contantType = "text/plain"
        post1.content = "Test Content 1"
        post1.category = "Category 1"
        post1.publish_time = timezone.now
        post1.visibility = "PUBLIC"
        post1.unlisted = False
        post1.save()

        post_id2 = uuid.uuid4()
        post2 = Post()
        post2.post_id = uuid.uuid4()
        post2.user_id = chengze
        post2.title = "Test Title 2"
        post2.description = "Test Description 2"
        post2.source = ""
        post2.origin = ""
        post2.contantType = "text/plain"
        post2.content = "Test Content 2"
        post2.category = "Category 2"
        post2.publish_time = timezone.now
        post2.visibility = "PRIVATE"
        post2.unlisted = True
        post2.save()

    def test_Post_attribute(self):
        post1 = Post.objects.get(post_id=post_id1)
        post2 = Post.objects.get(post_id=post_id2)
        self.assertEqual(post1.title, "Test Title 1")
        self.assertEqual(post1.description, "Test Description 1")
        self.assertEqual(post1.content, "Test Content 1")
        self.assertEqual(post1.category, "Category 1")
        self.assertEqual(post1.visibility, "PUBLIC")
        self.assertEqual(post1.unlisted, False)

        self.assertEqual(post2.title, "Test Title 2")
        self.assertEqual(post2.description, "Test Description 2")
        self.assertEqual(post2.content, "Test Content 2")
        self.assertEqual(post2.category, "Category 2")
        self.assertEqual(post2.visibility, "PRIVATE")
        self.assertEqual(post1.unlisted, True)

    def test_Post_Upload_Image(self):
        pass
