from django.contrib import admin
from .models import *

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user_id','displayName']
# Register your models here.
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(PostVisibeTo)
admin.site.register(Follow)
admin.site.register(FriendRequest)
