from django.test import TestCase
from accounts.models import *
from django.contrib.auth.models import User
import uuid

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
