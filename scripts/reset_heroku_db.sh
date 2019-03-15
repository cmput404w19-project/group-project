heroku restart
heroku pg:reset DATABASE --confirm cmput404w19-project
heroku run --app cmput404w19-project python manage.py migrate
heroku run --app cmput404w19-project python manage.py createsuperuser
