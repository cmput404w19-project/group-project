# accounts/urls.py
from django.urls import path
from . import views # from current directory to look for views file

# has to be called urlpatterns 
urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
]