# PiDrive

Ever needed to have a bunch of different USB drives connected to a machine, but that machine is far away? Or do you want to automate backups to an external drive that can be stored anywhere? PiDrive is for you!

PiDrive uses the USB-Gadget abilities of the Pi Zero and Pi 4 (and potentially other SBCs) to emulate a sparse file backed USB drives that can be stored on the Pi, Network Storage, a physical HDD, or really anywhere you want! All manageable by a Flask web UI/API (based on tedivm's flask starter app). 

# THIS CODE IS IN ALPHA
The mount/unmount and creation of USB drives is working, but has not been tested in production
Use at your own risk. I'm not responsible for lost data, exploded hardware, or anything else. You have been warned!


## Installation
Tested on Rasbian Lite on a Pi Zero W with Python 3.7 (There's a bug in 3.8 that breaks the template currently)

* sudo apt install python3 python3-pip python3-venv libparted-dev
* sudo nano /boot/config.txt
* add "modules-load=dwc2" and "dtoverlay=dwc2" at bottom
* sudo nano /etc/modules
* add "dwc2"
* reboot!

* (From App Dir)
* python3 -m venv env
* source env/bin/activate
* pip install -r requirements.txt (Go get a beer or 2 while this runs)
* Update settings.py with desired settings
* make init_db
* python manage.py run



## Features

* Tested on Python 3.3, 3.4, 3.5, 3.6, and 3.7
* Full user management system.
* Server side session storage.
* An API system with API tokens and route decorators.
* Includes database migration framework (`alembic`, using `Flask-Migrate`)

## Configured Extensions and Libraries

With thanks to the following Flask extensions and libraries:
* [Beaker](https://beaker.readthedocs.io/en/latest/) for caching and session management.
* [Celery](http://www.celeryproject.org/) for running asynchronous tasks on worker nodes.
* [Click](https://click.palletsprojects.com/) for the creation of command line tools.
* [Flask](http://flask.pocoo.org/) the microframework framework which holds this all together.
* [Flask-Login](https://flask-login.readthedocs.io/) allows users to login and signout.
* [Flask-Migrate](https://flask-migrate.readthedocs.io/) integrates [Alembic](http://alembic.zzzcomputing.com/) into Flask to handle database versioning.
* [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org) integrates [SQLAlchemy](https://www.sqlalchemy.org/) into Flask for database modeling and access.
* [Flask-User](http://flask-user.readthedocs.io/en/v0.6/) adds user management and authorization features.
* [Flask-WTF](https://flask-wtf.readthedocs.io/en/stable/) integrates [WTForms](https://wtforms.readthedocs.io) into Flask to handle form creation and validation.

In addition the front end uses the open source versions of:
* [Bootstrap](https://getbootstrap.com/)
* [CoreUI](https://coreui.io/)
* [Font Awesome](https://fontawesome.com/)


## Unique Features

* Database or LDAP Authentication - Applications built with this project can use the standard database backed users or can switch to LDAP authentication with a few configuration settings.

* API Authentication and Authorization - this project can allow people with the appropriate role to generate API Keys, which in turn can be used with the `roles_accepted_api` decorator to grant API access to specific routes.

* Versatile Configuration System - this project can be configured with a combination of configuration files, AWS Secrets Manager configuration, and environmental variables. This allows base settings to be built into the deployment, secrets to be managed securely, and any configuration value to be overridden by environmental variables.

* A [Celery](http://www.celeryproject.org/) based asynchronous task management system. This is extremely useful for long running tasks- they can be triggered in the web interface and then run on a worker node and take as long as they need to complete.

## Configuration

### Application configuration

To set default configuration values on the application level- such as the application name and author- edit `./app/settings.py`. This should be done as a first step whenever using this application template.

### Configuration File

A configuration file can be set with the environmental variable `APPLICATION_SETTINGS`.


### Environmental Variables

Any environmental variables that have the same name as a configuration value in this application will automatically get loaded into the app's configuration.

### Configuring LDAP

Any installation can run with LDAP as its backend with these settings.

```
USER_LDAP=true
LDAP_HOST=ldap://ldap
LDAP_BIND_DN=cn=admin,dc=example,dc=org
LDAP_BIND_PASSWORD=admin
LDAP_USERNAME_ATTRIBUTE=cn
LDAP_USER_BASE=ou=users,dc=example,dc=org
LDAP_GROUP_OBJECT_CLASS=posixGroup
LDAP_GROUP_ATTRIBUTE=cn
LDAP_GROUP_BASE=ou=groups,dc=example,dc=org
LDAP_GROUP_TO_ROLE_ADMIN=admin
LDAP_GROUP_TO_ROLE_DEV=dev
LDAP_GROUP_TO_ROLE_USER=user
LDAP_EMAIL_ATTRIBUTE=mail
```


## Initializing the Database

    # Initialize the database. This will create the `migrations` folder and is only needed once per project.
    make init_db

    # This creates a new migration. It should be run whenever you change your database models.
    make upgrade_models



## Acknowledgements

<!-- Please consider leaving this line. Thank you -->
[Flask-Dash](https://github.com/twintechlabs/flaskdash) was used as a starting point for this code repository. That project was based off of the [Flask-User-starter-app](https://github.com/lingthio/Flask-User-starter-app).

## Authors
- Robert Hafner (tedivms-flask) -- tedivm@tedivm.com
- Matt Hogan (flaskdash) -- matt AT twintechlabs DOT io
- Ling Thio (flask-user) -- ling.thio AT gmail DOT com
