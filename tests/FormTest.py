from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client
from accounts.forms import *
from accounts.models import *
import uuid

class EditProfileFormTest(TestCase):
    
    def setUp(self):
        #user = User.objects.create_user(username='kehan_wang', email="kehan1@ualberta.ca",password="Mypossword123")
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
        self.user=kehan1


    def test_editProfile(self):
        
        form = EditProfileForm(data={'displayName': 'kehan_wang', 
                                    'bio':'bio',
                                    'host':'host',
                                    'github':'https://github.com/cmput404w19-project/group-project',
                                    'url':'https://github.com/cmput404w19-project/group-project'})
        self.assertTrue(form.is_valid())


class NewPostFormTest(TestCase):
    
    def setUp(self):

        thisId = uuid.uuid4()
        kehan1 = UserProfile()
        kehan1.author_id=thisId 
        kehan1.user_id = User.objects.create_user(username='kehan_wang', email="kehan1@ualberta.ca",password="Mypossword123")
        kehan1.displayName="kehan1"
        kehan1.bio="bio"
        kehan1.host="host"
        kehan1.github="https://github.com/cmput404w19-project/group-project/projects",
        kehan1.url="https://github.com/cmput404w19-project/group-project/projects"
        kehan1.save()
        self.user = kehan1

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
        self.post=post1

    def test_Post(self):
        form = EditProfileForm(data={'user_id': self.user.user_id,
                                    'title':'title',
                                    'description':'description',
                                    'source':'https://github.com/cmput404w19-project/group-project',
                                    'origin':'https://github.com/cmput404w19-project/group-project',
                                    'contentType':'text/plain',
                                    'content':'content',
                                    'category':'category',})
        self.assertFalse(form.is_valid())
        #self.assertFalse(form.is_valid())