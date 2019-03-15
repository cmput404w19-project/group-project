from django.db import models
from django.contrib.auth.models import User # default user table in Django auth
from django.db.models.signals import post_save
from django.utils import timezone
import uuid

# Create your models here.

# Reference: Django model documentations
#https://docs.djangoproject.com/en/2.1/topics/db/models/ 


class UserProfile(models.Model):
    """
    User Information
    """
    # userprofile id
    author_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # user id
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
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
    def __str__(self):
        return str(self.user_id)




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
    user_id = models.ForeignKey(UserProfile,on_delete=models.CASCADE)

    # title
    title = models.CharField(max_length=80,default="")
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
    category = models.CharField(max_length=80, default="")
    # size: page size
    # published: timestamp ISO
    publish_time = models.DateTimeField(default=timezone.now)
    # visibility: ["PUBLIC","FOAF","FRIENDS","PRIVATE","SERVERONLY"]
    visibility = models.CharField(max_length=20, default="PUBLIC", choices=visibilityChoice)
    # unlisted: unlisted means it is public if you know the post name -- use this for images, it's so images don't show up in timelines
    unlisted = models.BooleanField(default=False)

    # Refereces about upload and load img/files
    # https://developer.mozilla.org/en-US/docs/Web/API/FileReader
    # https://stackoverflow.com/questions/17710147/image-convert-to-base64
    # https://github.com/Hipo/drf-extra-fields#base64filefield
    # image64: store image
    image64 = models.ImageField(upload_to='usr_img/', default="")
    # image64: store image NOT FINISHED
    file64 = models.FileField(upload_to='usr_file/', default="")
    # refPost: a text post can ref to a image post
    refPost = models.CharField(max_length=200, default="")


    def __str__(self):
            return self.title

class PostVisibleTo(models.Model):
    """
    Each Post visible to
    visibleTo: [] list of author URIs who can read the PRIVATE message
    """
    # Post id
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    # user id : who can see the post
    user_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

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
    user_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    # comment
    content = models.CharField(max_length=100, default="")
    # contentType
    contentType = models.CharField(max_length=20, choices=typeChoice, default="text/plain")
    # published
    publish_time = models.DateTimeField(default=timezone.now)
    # post id (maybe?)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)



class Follow(models.Model):
    """
    Follow Relationship Between Users
    Friendship exist if A follows B and B follows A
    """
    # follower  Foreign key to user
    follower_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="follower")
    # following Foreign key to user
    following_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="following")
    # Time follow starts
    follow_publish_time = models.DateTimeField(default=timezone.now)
    class Meta:
        unique_together = ("follower_id", "following_id")


class FriendRequest(models.Model):
    """
    Friend request status
    """
    statusChoice = (
        ("Accept","Accept"),
        ("Decline","Decline"),
        ("Pending","Pending")
    )
    # requested by id  Foreign key to user
    requestedBy_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='requestedBY')
    # request to id  Foreign key to user
    requestedTo_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='requestedTO')
    # request status
    request_status = models.CharField(max_length=20, choices=statusChoice, default="Pending")
    # Request Time
    request_publish_time = models.DateTimeField(default=timezone.now)
    # Primary key(user 1 , user 2)
    class Meta:
        unique_together = ("requestedBy_id", "requestedTo_id")



class Images(models.Model):
    """
    Image In The Post
    """
    # post id  Foreign key to Post
    # path to image
    pass


# using signal to tigger to create
# https://simpleisbetterthancomplex.com/tutorial/2016/07/28/how-to-create-django-signals.html
# author: Vitor Freitas
def create_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = UserProfile.objects.create(user_id=kwargs['instance'], displayName=kwargs['instance'].username)
        if not kwargs['instance'].is_staff:
            kwargs['instance'].is_active = False
            kwargs['instance'].save()

post_save.connect(create_profile, sender=User)
