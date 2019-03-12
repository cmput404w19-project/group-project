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
from django.urls import path, include
from django.conf.urls import url, include
from django.views.generic.base import TemplateView
from accounts import views

from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls

router=DefaultRouter()
router.register('users', views.UserViewSet)

urlpatterns = [
    # the basic homepage
    path('', views.home, name='home'),

    # admin paths
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='signup')), # when url request for accounts/ , it will go to accounts.urls
    path('accounts/', include('django.contrib.auth.urls')),

    # Api docs
    path('docs/', include_docs_urls(title='API Docs')),

    # all public 
    path(r'posts/', views.PublicPosts().as_view()),

    # handle get/post for author posting
    path(r'author/posts', views.AuthorPosts().as_view()),
    # author endpoints
    path(r'author/<str:author_id>', views.AuthorProfile().as_view()),

    # post endpoints
    path(r'posts/<str:post_id>', views.PostById().as_view())

]
