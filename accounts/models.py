from django.db import models
from django.contrib.auth.models import User # default user table in Django auth
from django.db.models.signals import post_save

# Create your models here.
class UserProfile(models.Model):
	"""
	User Information
	"""
	# user id
	user_id = models.OneToOneField(User,on_delete=models.CASCADE, primary_key=True)
	# user name
	displayName = models.CharField(max_length=20, default="") 
	# 
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
	# post id  Unique Primary key
	# author   Foreign key to user
	# title
	# description
	# source
	# origin
	# content type      -text/markdown -application/base64 -image/png;base64 -image/jpeg;base64
	# content ?
	# categories
	# size: page size
	# published: timestamp ISO
	# visibility: ["PUBLIC","FOAF","FRIENDS","PRIVATE","SERVERONLY"]
	# visibleTo: [] list of author URIs who can read the PRIVATE message
	# unlisted: unlisted means it is public if you know the post name -- use this for images, it's so images don't show up in timelines
	pass

class PostVisibeTo(models.Model):
	"""
	Each Post visible to
	"""
	# Post id
	# user id : who can see the post
	pass


class Comment(models.Model):
	"""
	Comments About the Post
	"""
	# author   Foreign key to user
	# comment  
	# contentType
	# published
	# post id (maybe?)
	pass

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