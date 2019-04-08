"""Cmput404Project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls import url, include
from django.views.generic.base import TemplateView
from accounts import views

from django.contrib.auth.decorators import login_required

from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls

from rest_framework_swagger.views import get_swagger_view

from core import settings
from django.views.static import serve
from django.conf.urls.static import static

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib.auth.decorators import login_required

router=DefaultRouter()
router.register('users', views.UserViewSet)

schema_view = get_schema_view(
   openapi.Info(
      title="404-project API Docs",
      default_version='v1',
      description="The API docs for our 404 project",
      license=openapi.License(name="Apache 2.0"),
   ),
   public=True,
)

urlpatterns = [
    # the basic homepage
    path('', views.home, name='home'),

    # admin paths
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='signup')), # when url request for accounts/ , it will go to accounts.urls
    path('accounts/', include('django.contrib.auth.urls')),

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # API Endpoints
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # We have both / and no slash to be a little more flexible

    # Api docs
    path(r'docs/', schema_view.with_ui('swagger')),

    path(r'posts/', views.Posts().as_view()),
    path(r'posts', views.Posts().as_view()),

    path(r'posts/<str:post_id>/', views.PostById().as_view()),
    path(r'posts/<str:post_id>', views.PostById().as_view()),

    path(r'author/posts/', views.AuthorPosts().as_view()),
    path(r'author/posts', views.AuthorPosts().as_view()),

    path(r'author/<str:author_id>/', views.AuthorProfile().as_view()),
    path(r'author/<str:author_id>', views.AuthorProfile().as_view()),

    path(r'author/<str:author_id>/posts/', views.AuthorPostsById().as_view()),
    path(r'author/<str:author_id>/posts', views.AuthorPostsById().as_view()),

    path(r'author/<str:author_id>/friends/', views.FriendListByAuthorId().as_view()),
    path(r'author/<str:author_id>/friends', views.FriendListByAuthorId().as_view()),

    path(r'author/<str:author1_id>/friends/<path:author2_id>/', views.CheckFriendStatus().as_view()),
    path(r'author/<str:author1_id>/friends/<path:author2_id>', views.CheckFriendStatus().as_view()),

    path(r'posts/<str:post_id>/comments/', views.CommentsByPostId().as_view()),
    path(r'posts/<str:post_id>/comments', views.CommentsByPostId().as_view()),

    path(r'friendrequest/', views.FriendRequestNew().as_view()),
    path(r'friendrequest', views.FriendRequestNew().as_view()),
    path(r'internal/friendrequest', views.InternalFriendRequest().as_view()),
    path(r'internal/friendrequest/', views.InternalFriendRequest().as_view()),
    path(r'deletefriendrequest/', views.deleteFriendRequest().as_view()),
    path(r'deletefriendrequest', views.deleteFriendRequest().as_view()),
    path(r'acceptfriendrequest/', views.acceptFriendRequest().as_view()),
    path(r'acceptfriendrequest', views.acceptFriendRequest().as_view()),


    #unfollow
    path(r'unfollowrequest/', views.UnFollow().as_view()),
    path(r'unfollowrequest', views.UnFollow().as_view()),

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Internal API Endpoints
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    path(r'externalendpoints/', views.ExternalEndpoints().as_view()),
    path(r'externalendpoints', views.ExternalEndpoints().as_view()),

    # # the render of making new post
    path(r'author/render/post/', login_required(views.MakePost().as_view(),login_url="/accounts/login/"), name='render_post'),
    path(r'author/render/post', login_required(views.MakePost().as_view(),login_url="/accounts/login/"), name='render_post'),

    # the render of showing all posts for specific user
    path(r'author/<str:author_id>/render/posts/', views.ShowMyPosts),
    path(r'author/<str:author_id>/render/posts', views.ShowMyPosts),

    path(r'author/<str:author_id>/render/posts/posts/', views.ShowMyPosts),
    path(r'author/<str:author_id>/render/posts/posts', views.ShowMyPosts),

    # the render of showing a specific post for specific user
    path(r'posts/<str:post_id>/render/', views.RenderPostByID),
    path(r'posts/<str:post_id>/render', views.RenderPostByID),


    path(r'post/delete/<str:post_id>', views.postDelete().as_view(), name='deletepost'),
    path(r'post/edit/<str:post_id>', views.EditPost().as_view(),name='editpost'),

    #path(r'author/<str:author_id>/render/posts/frontend/author/github/', views.GitHubView().as_view()),
    #path(r'author/<str:author_id>/render/posts/frontend/author/github', views.GitHubView().as_view()),

    path(r'author/<str:author_id>/render/posts/frontend/author/github/', views.GitHubView.as_view()),
    path(r'author/<str:author_id>/render/posts/frontend/author/github', views.GitHubView.as_view()),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Reference
# https://stackoverflow.com/questions/5517950/django-media-url-and-media-root
