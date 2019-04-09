CMPUT404-Winter-2019-Group-Project-socialdistribution
===================================
[![Build Status](https://travis-ci.org/cmput404w19-project/group-project.svg?branch=master)](https://travis-ci.org/cmput404w19-project/group-project)


## The project is running on Heroku
https://cmput404w19-web-project.herokuapp.com

Demo Video
========================
https://youtu.be/R4Q9EsSoSQ4

Contributors / Licensing
========================

Contributors:

    Chengze Li (chengze2@ualberta.ca)
    Frederic Sauve-Hoover (rsauveho@ualberta.ca)
    Xinrui Lu (xinrui7@ualberta.ca)
    Kehan Wang (kehan1@ualberta.ca)
    Zhaozhen Liang (zhaozhen@ualberta.ca)

# Installation
Create a virtualenv and activate the python virtual environment
```
> virtualenv venv --python=python3
> source venv/bin/activate
```
Download the project and install all libraries that are needed
```
> https://github.com/cmput404w19-project/group-project.git 
> pip install -r requirments.txt
```
Migrate all the changes if there are any 
</br>and create superuser (this will be the admin on server)
</br>and then we can run the server on localhost
```
> python manage.py migrate
> python manage.py createsuperuser
> python manage.py runserver
```
If you made any changes to the Django model, please run the follow to commiting all those changes to the actual SQL database
```
> python manage.py makemigrations
> python manage.py migrate
```

# How to get an account?
You will first need to get into the signup page and register an account. And then **you will need to wait for one of the Admin to give you permission to log into the main home page.** Or you can create a super user which will be the admin on the server as default. But other new sign up users will still need to grant permission to access the home page(login).
</br>
</br>For accepting new sign up user's request for granting permission to access homepage(login), you must first have a super user account and then go to the admin page by "/admin" and then go to the User table and find the users you want to grant permission to and click into it and check the **is_active** 


# AJAX Documentation
We decide to use lot of the AJAX on the client side for the purposes of sharing the server work load.
### Home Page posts
We have a heavy AJAX in our client side front end. We use for loop AJAX fetches and promise.all() to send all requests to all the servers(External endpoints and also our own server) APIs (/author/posts) for getting all the visible posts for that particular user  
### Home Page posting comments
We send the comment post request to the server(the one which is hosting that post) API by fetch
### AuthorProfile
For author profile, we pre-render the author url into the html before return to the client. And then the client side Javascript will send fetch request to the server that is hosting the author information (by that url)
### Friend
We use fetch to send request to get the list of friends for that particular user in the friend page front end when user is viewing the friend list page


# Design and Idea
So the project theme is distributive social network, we follow the specification idea that each server is independent from each other and hosting only the posts information that is made by its own server user and also hosting each own server user's userprofile. Each server does not store any extra information about other server's user and posts except we store the url(api) that we can request for the data.

## Friends
In this project, the definition of real friend is if two users are following each other. Our way of handling friend is to only keep one direction followship in each server. Each server will only store who their user is following but does not know who is following them since the other server will have that. In such way, handling friends across different servers are actually way easier. When validating friend lists we send request to other servers to verify if that user is also following him/her to get the two diretion followships. 

## External endpoints
For dealing with external endpoints, we use baisc auth which is provided by Django CRFS token for authentications to access APIs. And we have a model table to keep all the external servers information (hostname,username,password) that we are connecting to.

# References
### TestCase
Answered by Pedro M Duarte:
</br>https://stackoverflow.com/questions/2619102/djangos-self-client-login-does-not-work-in-unit-tests<br/>
https://docs.djangoproject.com/en/2.1/topics/testing/overview/<br/>
https://django-testing-docs.readthedocs.io/en/latest/index.html<br/>
### Login and Logout tutorial
author: Will Vincent
<br/>https://wsvincent.com/django-user-authentication-tutorial-login-and-logout/
<br/>https://wsvincent.com/django-user-authentication-tutorial-signup/
<br/>https://wsvincent.com/django-user-authentication-tutorial-password-reset/
### Model:
#### models
Reference: **Django model documentations**
https://docs.djangoproject.com/en/2.1/topics/db/models/
#### Upload
https://stackoverflow.com/questions/17710147/image-convert-to-base64<br/>
https://github.com/Hipo/drf-extra-fields#base64filefield<br/>
### Create UserProfile by Signal:
author: Vitor Freitas
https://simpleisbetterthancomplex.com/tutorial/2016/07/28/how-to-create-django-signals.html
### Views:
cutteeth https://stackoverflow.com/questions/40191931/django-how-to-use-request-post-in-a-delete-view
</br>Django class-based view documentation:
</br>https://docs.djangoproject.com/en/2.1/topics/class-based-views/
<br>https://www.django-rest-framework.org/tutorial/3-class-based-views/
<br>http://www.chenxm.cc/article/244.html
<br>http://webdocs.cs.ualberta.ca/~hindle1/2014/07-REST.pdf
<br>https://stackoverflow.com/questions/24971729/django-python-todataurl-return-a-response-with-the-string-from-todataurl
<br>https://segmentfault.com/a/1190000010970988
### Decorator for checking Login require and annoymous require
Django decorator documentation:
</br>https://docs.djangoproject.com/en/2.1/_modules/django/contrib/auth/decorators/
</br>annoymous require:
</br>author: yetty  https://djangosnippets.org/users/yetty/
</br>https://djangosnippets.org/snippets/2969/
### HTML:
https://fonts.google.com/?selection.family=Muli|Sniglet|Srisakdi
<br/>https://www.w3schools.com/css/css_inline-block.asp
<br/>https://www.w3schools.com/css/tryit.asp?filename=trycss_inline-block_span1
<br/>https://www.w3schools.com/cssref/pr_class_position.asp
<br/>https://www.w3schools.com/cssref/tryit.asp?filename=trycss_position_relative
<br/>https://www.w3schools.com/cssref/tryit.asp?filename=trycss_font-style
<br/>Author:Phrogz
<br/>https://stackoverflow.com/questions/5067279/how-to-align-this-span-to-the-right-of-the-div
<br/>https://stackoverflow.com/questions/21376788/how-to-display-3-buttons-on-the-same-line-in-css
<br/>https://www.w3schools.com/w3css/tryit.asp?filename=tryw3css_templates_social&stacked=h
<br/>https://www.zmrenwu.com/post/8/
<br/>Author:dusai
<br/>https://zhuanlan.zhihu.com/p/44939567
<br/>https://www.w3schools.com/bootstrap/bootstrap_button_groups.asp
<br/>Django Documentation
<br/>https://docs.djangoproject.com/zh-hans/2.1/
<br/>http://www.permadi.com/tutorial/jsInnerHTMLDOM/index.html
<br/>https://github.com/dispersal/CMPUT404-project-socialdistribution/blob/master/posts/static/author/author_posts.js
<br/>https://www.w3schools.com/jsref/event_onclick.asp
<br/>https://stackoverflow.com/questions/46630893/angular-res-json-is-not-a-function
<br/>https://developers.google.com/web/updates/2015/03/introduction-to-fetch
<br/>https://stackoverflow.com/questions/351409/how-to-append-something-to-an-array
<br/>https://docs.djangoproject.com/en/2.1/ref/csrf/
<br/>https://stackoverflow.com/questions/36131472/django-csrf-token-with-js
<br/>https://stackoverflow.com/questions/1795701/django-reverse-for-javascript
<br/>https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch

### Post
#### Handle Markdown
https://github.com/showdownjs/showdown<br/>
https://github.com/showdownjs/showdown/wiki/Tutorial:-Markdown-editor-using-Showdown<br/>
#### css
https://www.jianshu.com/p/db2620e94a9b<br/>
#### Hidden Fields
https://ilusm.iteye.com/blog/232236<br/>
#### Read File/Image
https://developer.mozilla.org/en-US/docs/Web/API/FileReader/readAsDataURL<br/>
#### Static Media Path
https://docs.djangoproject.com/en/2.1/howto/static-files/<br/>
https://stackoverflow.com/questions/5517950/django-media-url-and-media-root<br/>
#### base64 padding
https://stackoverflow.com/questions/2941995/python-ignore-incorrect-padding-error-when-base64-decoding/49459036<br/>
#### Form
https://www.itgank.com/archives/2557<br/>
https://stackoverflow.com/questions/604266/django-set-default-form-values<br/>
#### Api
https://www.django-rest-framework.org/tutorial/3-class-based-views/<br/>
http://www.chenxm.cc/article/244.html<br/>
http://webdocs.cs.ualberta.ca/~hindle1/2014/07-REST.pdf<br/>
https://segmentfault.com/a/1190000010970988<br/>

License
=======================
Generally everything is LICENSE'D under the Apache 2 license by Frederic Sauve-Hoover, Kehan Wang, Chengze Li, Zhaozhen Liang, Xinrui Lu
