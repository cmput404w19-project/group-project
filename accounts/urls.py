# accounts/urls.py
from django.urls import path
# from django.conf.urls import url
from . import views # from current directory to look for views file

app_name = 'accounts'
# has to be called urlpatterns
urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    #path('rest/', views.User.as_view()),
    # url(r'^signup/$', views.SignUp.as_view(), name='signup'),
 	path('profile/', views.profile, name='profile')   
]
