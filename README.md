# oidc_django_demo
This is a small Django project to demonstrate using private keys and OpenID Connect

## What you'll build
You'll build a Django application with a login backed by OpenID Connect

## What you'll need
 - [Django](https://www.djangoproject.com/) : This project uses version 1.11.5
 - [Python](https://www.python.org) : We'll use python version 3.5.2 or later

## Create an unsecured web application
It may be helpful to set up a [virtualenv](https://virtualenv.pypa.io/en/stable/) to isolate the
setup for this project. (There are several tutorials on how to use it, so I'm not going to document that here)

The following is a shortened form of the [offical Django tutorial](https://docs.djangoproject.com/en/1.11/intro/tutorial01/).

### Install Django
```
(python_3.5)$ pip install Django
```

### Create a 'site'
Django 'sites' can be thought of as a project that contains one or more appliations under them.
```
(python_3.5)$ django-admin startproject mysite 
```

This will create the following:
```
mysite/
    manage.py
    mysite/
        __init__.py
        settings.py
        urls.py
        wsgi.py
```

### Create an app
We'll create our 'app' under the site.
```
(python_3.5)$ cd mysite
(python_3.5) mysite$ python manage.py startapp simpleapp
```

This will create a subdirectory called `simpleapp` containing your new app
It's structure will look like:
```
simpleapp/
    __init__.py
    admin.py
    apps.py
    migrations/
        __init__.py
    models.py
    tests.py
    views.py
```

### Create a view
We'll do three things to create our `index` view for our application.
1. Modify `simpleapp/views.py`
1. Create a template at `simpleapp/templates/simpleapp.html`
1. "Install" the app into our Django site

#### Modify `simpleapp/views.py`
Django created the file for us, but it only contains an import.
Change it to look like:
```python
from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, "simpleapp.html")
```
This will simply forward to the template we're about to create

#### Create a template
In this simple case our template is just going to be an HTML file since our application isn't really doing anything.
You can read up on [using Django templates here](https://djangobook.com/django-templates/)

For now just create the `simpleapp/templates` directory and add in `simpleapp.html` so it looks like:
```html
<!DOCTYPE html>
<html>
<head lang="en">
    <meta charset="UTF-8">
    <title>simpleapp</title>
</head>
<body>
<p>Hello, world. You're at the simpleapp index.</p>
</body>
</html>
```

#### Set up the urls for Django
While this isn't needed for our super simple application at this point, it will be later on.
We have to define which URL patterns go to which views. Add in a `simpleapp/urls.py` file that looks like:
```python
from django.conf.urls import url

from . import views

urlpatterns = [
  url(r'^$', views.index, name='index'),
]
```

#### "Install" the app into our Django project
In order for Django to know about the template, we have to 'install' the application.
To do this we'll add it to the `mysite/mysite/settings.py` file.
Open that file, and find the `INSTALLED_APPS` variable. Add in our `simpleapp` like so:
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'simpleapp'
]
```
Now we need to tell our project about the `simpleapp` URLs.
Modify the `mysite/urls.py` file to look like:
```python
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^simpleapp/', include('simpleapp.urls')),
    url(r'^admin/', admin.site.urls),
]
```

### Run the server
Now we can test out our application.
Run the following from the top level `mysite` directory where `manage.py` lives:
```
(python_3.5) mysite$ python manage.py runserver
```

Once that is done you should be able to visit your new application at [http://localhost:8000/simpleapp](http://localhost:8000/simpleapp)

#### You'll find the output of this part in `inital_site`

## Securing your application with OIDC

In this section we'll
1. Install and setup `django-oidc`
2. Create a protected portion of our web application

### Install `django-oidc`
`django-oidc` is a module for Django that allows authentication to happen via OpenID Connect.
The problem with it is there are many forks of the project that have different feature sets.
The fork located at [https://github.com/koriaf/django-oidc](https://github.com/koriaf/django-oidc) seems to be the best 
version for working with Python 3 and Django 1.11. It has also been updated with a modifcation to support `private_key_jwt`
based client authentication.

As a note, `django-oidc` is basically a wrapper around the [https://github.com/OpenIDC/pyoidc](https://github.com/OpenIDC/pyoidc)
project that is a generic python module for using OpenID connect.

To install the version of `django-oidc` we want we'll use `pip`:
```
(python_3.5) mysite$ pip install git+https://github.com/koriaf/django-oidc.git
```
### Configure our Django project ot use `django-oidc`
To configure our project we'll have to
1. Install `django-oidc` in `mysite/settings.py`
1. Add the urls to `mysite/urls.py`
1. Define our OP and Client
1. Set up our private keys for client authentication

#### Install `django-oidc` into our project
We'll 'install' the module the same way we installed our `simpleapp` in `mysite/settings.py`
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djangooidc',
    'simpleapp'
]
```
NOTE: The application does not contain the '-' when you install it, just add `djangooidc` to the `INSTALLED_APPS`

#### Set up the OpenID Connect URLS
Thankfully `django-oidc` has already defined all the appropriate call back URLs, etc. We just have to tell our project 
how to use them. This is done in the `mysite/urls.py` file.

```python
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^simpleapp/', include('simpleapp.urls')),
    url(r'^openid/', include('djangooidc.urls')),
    url(r'^admin/', admin.site.urls),
]
```

#### Define our OP and Client
All the configuration for using OIDC will be in the `mysite/settings.py` file

First we add in the `AUTHENTICATION BACKENDS`, this isn't in the default `settings.py` so we'll put it after the `DATABASES`
setup. We need the default `ModelBackend` as well as our `OpenIdConnectBackend`.
We'll also set up the `LOGIN_URL` while we're here. By default this can just be `/openid` but that will bring you to a 
login that allows you to select which OpenID provider, or figure it out from typing in an email, etc. in a form that can be customize

Since we're going to only set up a single OpenID Connect provider, and only want to use that one though,
we can use the pattern of `/openid/openid/<providername>`, where `<providername>` is defined when we configure the 
provider, `mitreid` in this particular case.
 
```python
# DEFINE AUTHENTICATION_BACKENDS
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'djangooidc.backends.OpenIdConnectBackend'
]

# Set LOGIN_URL (for django oidc)
LOGIN_URL = '/openid/openid/mitreid'
```

Next we'll want to set up the `PyOIDC` settings
The version provided here has several options commented out, so we'll only focus on the core ones here.
Add all of these to the `mysite/settings.py` file
```python
# We're disabling dynamic client registration.
OIDC_ALLOW_DYNAMIC_OP = False

# Default OIDC behavoir will be the 'code' workflow
OIDC_DEFAULT_BEHAVIOUR = {
    "response_type": "code",
    "scope": ["openid", "profile", "email", "address", "phone"],
}

# Set up our providers. Here the name is 'mitreid' which we use in the login URL above
OIDC_PROVIDERS = {
    "mitreid": {
        "srv_discovery_url": "https://mitreid.org/",
        "behaviour": OIDC_DEFAULT_BEHAVIOUR,
        "client_registration": {
            "client_id": "f5458edf-5163-4b3b-a965-577922719fb1",
            "redirect_uris": ["http://localhost:8000/openid/callback/login/"],
            'token_endpoint_auth_method': ['private_key_jwt'],
            "enc_kid": "rsa_test",
            "keyset_jwk_file": "file://keys/keyset.jwk"
        }
    }
}
```

The important bit here is the Providers setup. We are defining only one provider (`mitreid`), and we are not using 
dynamic client registration. We have a `sev_discovery_url` that allows `pyoidc` to find all the endpoints for us, look 
in the comments to see how to manually specify those if needed.

We then use `client_registration` to define our client. We have the `client_id` which matches the `client id` on your 
OIDC server. The `redirect_uris` should contain only one, which is defined by `django-oidc` as `http://<server>:<port>/openid/callback/login`.

The next three values, `token_endpoint_auth_method`, `enc_kid`, and `keyset_jwk_file` are all used to set up using
private keys for client authentication rather than a `client_secret`.

`token_endpoint_auth_method` is pretty self explaintory, we're using `private_key_jwt`.

`enc_kid` must match the `kid` in the JWK file for the key pair used when setting up the client on your OIDC provider.
(Here we need both the private and public key, where the provider should only have the public.)

`keyset_jwk_file` specifies the keyset file that should be used. (Where the `kid` lives.)

#### Set up private keys
We'll place the encryption keys in `/mysite/keys`. We only need a Key Set, which should look like:
```json
{
  "keys": [
    {
      "kty": "RSA",
      "d": "CzY14i8NxPUAPmH9JHR5VIMezv0WOunBB0NkfZmzUGrJSn5DXGrRIs0psERyHLSBKVTpRGcp9ZlcDfMZV81e-v1a_sz9IogCNd15y4UUcpFKuAKAY0s4Fa8whu3u7iL0Zut_tKlBxKPhAtgX3Urc6neRURFvhfzD4zrOaKRbZwf446JxrqyyDSQfGUBhTkiURsvvch0GojaUS-hzuI8tRzgowC5K8jHrl8Bg__ai7iuNfHOFxH83oAlSM4fEt-Fi4FLpev2dxXhvL8sJOVN7CReDsxYWR7l1rzlzH_cER6uA2QX9xCYyqMCegdCfTEEaCGKr28LssRBiSCe6DylRgQ",
      "e": "AQAB",
      "use": "sig",
      "kid": "rsa_test",
      "alg": "RS256",
      "n": "lTmpgjt5cyV-0v0QWRdiarUZRd6U5muDRrqHOe1UwA6lZUD68LlfvwcYnR8cInMZd3o1Tmx4cvePP8zOCEBnlVVeAamxXaRT59w2iZyXyw90u9or-R3qAMtK-eObJH29jMjRog06U-TXzBExkRcyz8c3JIlI9t1eNMESsBQsrglwGFTa_PFqLM0sGEtuCs9L-Q9ca0-9rlounVhGJMKF4BNEbNoBLeoK-fcwsx45IKo-iId_vJTrK_lTGXy4VwQnR4uHzHWOtvx9h2PVdsaZcSgHk4aIyvN8B5SB2h6DVR1_QtBLwcbY5D-JNT1fMpQqGmYmVHW-AteO82YMpIaIjw"
    }
  ]
}
```

I've also included the Key pair and just the public key versions of the jwk in this directory for convenience.

**DO NOT USE THESE KEYS** - Generate your own. You can use a site like: [https://mkjwk.org/](https://mkjwk.org/) with a 
key length of 2048, key use of `signing`, and your own `kid` that you can specify in the client definition above.

### Create a protected portion of our web app
Now that we've set up `django-oidc` it's pretty simple to lock down parts of our web application.
At this point we'll want to `migrate` our project to set up the database. By default Django uses `sqlite3`, but doesn't
recommend that for production. For our little test here, it is just fine though.
Run the following to set up the user tables, etc.:
```
(python_3.5) mysite$ python manage.py migrate
```

Now we'll change our simple app template to show if we've logged in or not, and provide a link to a resource that only 
authenticated users can get to. Due to the default processors that Django has, we'll have a `user` object passed on to the
template automatically.

Modify `simpleapp/templates/simpleapp.html` so it looks like:
```html
<!DOCTYPE html>
<html>
<head lang="en">
    <meta charset="UTF-8">
    <title>{% block title %}{% endblock %}</title>
</head>
<body>
{% if user.is_authenticated %}
    <p>Welcome, {{ user.get_username }}. Thanks for logging in.</p>
{% else %}
    <p>Welcome, new user. Please log in.</p>
    <a href="{% url 'openid_with_op_name' op_name='mitreid' %}?next={{request.path}}">Log In</a>
{% endif %}
<br>
<p>Here is a link to a <a href="{% url 'protected' %}">protected resource</a></p>
</body>
</html>
```

If you look you'll see we have an if statement that determines if the user is logged in. If not, we 
provide a login link. Because of the way authentication works on Django, we have to give it a `next=` parameter
so it knows where to go. `{{request.path}}` resolves to the current path. The `openid_with_op_name` url will create
a link to login with a specific OIDC provider (in this case our `mitreid` one).

If we are logged in, we're just displaying the `user.get_username` value in a welcome message.

Next we'll define the `protected` view that the link at the bottom goes to.

First we'll modify `simpleapp/views.py` to create the view. add in the following imports and function.
```python
from django.contrib.auth.decorators import login_required

...

@login_required
def protected(request):
    return render(request, "protected.html")
```

That's it. The `@login_required` indicates that you can only get to this view if you are logged in.

Now we'll create the template as `simpleapp/templates/protected.html`.
```html
<!DOCTYPE html>
<html>
<head lang="en">
    <meta charset="UTF-8">
    <title>{% block title %}{% endblock %}</title>
</head>
<body>
<p><a href="{% url 'index' %}">Return</a></p>
<p>You should only see this if you are logged in.</p>
<table>
    <tr><td>user.get_username</td><td>{{user.get_username}}</td></tr>
    <tr><td>user.email</td><td>{{user.email}}</td></tr>
    <tr><td>user.first_name</td><td>{{user.first_name}}</td></tr>
    <tr><td>user.last_name</td><td>{{user.last_name}}</td></tr>
    <tr><td>user.username</td><td>{{user.last_login}}</td></tr>
</table>
</body>
</html>
```

And lastly we'll add `protected` to our urls. Change the `simpleapp/urls.py` to the following:
```python
from django.conf.urls import url

from . import views

urlpatterns = [
  url(r'^$', views.index, name='index'),
  url(r'^protected/$', views.protected, name='protected')
]
```

Fire up the application now with:
```
(python_3.5) mysite$ python manage.py runserver
```
Now when you go to [http://localhost:8000/simpleapp/](http://localhost:8000/simpleapp/) you should see that you are not 
logged in. You can either click the login link, or just click right on the `protected` link, and you should be re-directed 
to the `mitreid.org` OIDC login page. Once logged in, you should come back to this page or see the `protected` page with 
user information.

**NOTE:** going to `openid/logout` will attempt to end the session at the OIDC provider. This is not recommended as not 
all providers support this, plus it will log the user out of other applications.

You'll find the completed version of this tutorial in the `completed` sub directory.