# django_init

Init django project with user accounts, social login, correct settings

# Features

- Extends user models to accounts.User
- Integrate python-social-auth
- Bootstrap template
- Bootstrap form render
- Core test base
- Messages render
- Test coverage 100%
- Multiple settings module
- Heroku deployment available
- User account / profile
- Two factor authentication
- Celery Email
- Celery app


# Celery start

celery -A root worker -l info


# Note

Social login test will be run on server address `localhost:8180`
Change `TEST_COMMAND_EXTENDS` on CircleCI to modify test command
