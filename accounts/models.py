from django.db import models
from django.contrib.auth.models import User # default user table in Django auth
from django.db.models.signals import post_save
import uuid 

# Create your models here.
class UserProfile(models.Model):
	"""
	User Information
	"""
	# user id
	user_id = models.OneToOneField(User,on_delete=models.CASCADE, primary_key=True)
	# user name
	displayName = models.CharField(max_length=20, default="") 
	# bio
	bio = models.CharField(max_length=100, default="")
	# which server is hosting this user info
	host = models.CharField(max_length=50, default="")
	# github
	github = models.URLField(default="")
	# url
	url = models.URLField(default="")
	# indexes
	class Meta:
		indexes = [
			models.Index(fields=['user_id'], name='usr_idx'),
		]
    
	


class Post(models.Model):
	"""
	USER POST
	"""
	typeChoice = (
		('text/markdown', 'text/markdown'),
		('text/plain','text/plain'),
		('application/base64', 'application/base64'),
		('image/png;base64','image/png;base64'),
		('image/jpeg;base64','image/jpeg;base64')
	)
	visibilityChoice = (
		("PUBLIC","PUBLIC"),
		("FOAF","FOAF"),
		("FRIENDS","FRIENDS"),
		("PRIVATE","PRIVATE"),
		("SERVERONLY","SERVERONLY")
	)
	# post id  Unique Primary key
	post_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	# author   Foreign key to user
	author_id = models.ForeignKey(User,on_delete=models.CASCADE)
	# title
	title = models.CharField(max_length=20,default="")
	# description
	description = models.CharField(max_length=200,default="")
	# source
	source = models.URLField(default="")
	# origin
	origin = models.URLField(default="")
	# content type      -text/markdown -application/base64 -image/png;base64 -image/jpeg;base64
	contentType = models.CharField(max_length=20, choices=typeChoice, default="text/plain")
	# content ?
	content = models.TextField(default="")
	# categories
	category = models.CharField(max_length=20, default="")
	# size: page size
	# published: timestamp ISO
	publish_time = models.DateTimeField(auto_now_add=True, blank=True)
	# visibility: ["PUBLIC","FOAF","FRIENDS","PRIVATE","SERVERONLY"]
	visibility = models.CharField(max_length=20, default="PUBLIC", choices=visibilityChoice)
	# unlisted: unlisted means it is public if you know the post name -- use this for images, it's so images don't show up in timelines
	unlisted = models.BooleanField(default=False)

class PostVisibeTo(models.Model):
	"""
	Each Post visible to
	visibleTo: [] list of author URIs who can read the PRIVATE message
	"""
	# Post id
	post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
	# user id : who can see the post
	user_id = models.ForeignKey(User, on_delete=models.CASCADE)

	class Meta:
		unique_together = ("post_id", "user_id")


class Comment(models.Model):
	"""
	Comments About the Post
	"""
	typeChoice = (
		('text/markdown', 'text/markdown'),
		('text/plain','text/plain'),
		('application/base64', 'application/base64'),
		('image/png;base64','image/png;base64'),
		('image/jpeg;base64','image/jpeg;base64')
	)
	# comment id
	comment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	# author   Foreign key to user
	author_id = models.ForeignKey(User, on_delete=models.CASCADE)
	# comment  
	content = models.CharField(max_length=100, default="")
	# contentType
	contentType = models.CharField(max_length=20, choices=typeChoice, default="text/plain")
	# published
	publish_time = models.DateTimeField(auto_now_add=True, blank=True)
	# post id (maybe?)
	post_id = models.ForeignKey(Post, on_delete=models.CASCADE)

class Friendship(models.Model):
	"""
	Friend Relationship Between Users
	remember this is bi-directional relation
	AB <-> BA
	keep one relation tuple is enough for each relationship
	"""	
	# user 1 id  Foreign key to user
	# user 2 id  Foreign key to user
	# Create Date Time
	# Primary key(user 1 , user 2)
	pass

class Follow(models.Model):
	"""
	Follow Relationship Between Users
	"""
	# follower  Foreign key to user
	# following Foreign key to user
	pass

class Images(models.Model):
	"""
	Image In The Post
	"""
	# post id  Foreign key to Post
	# path to image
	pass

def create_profile(sender, **kwargs):
	if kwargs['created']:
		user_profile = UserProfile.objects.create(user_id=kwargs['instance'])


post_save.connect(create_profile, sender=User)