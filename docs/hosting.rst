Hosting the MedOps REST API
===========================

The MedOps API is built using Flask and can be hosted in any environment
that can proxy Flask applications. Included with this repository is
an example application in :code:`medos/app.py` that instantiates
the API blueprints to create a running task server and some configuration
files for hosting. The setup guide provided here is just one way to get
a server running. Obviously it's up to you if you want to change one
or more of the hosting decisions outlined here.

These instructions assume you are using a server running a Linux distribution
with an nginx webserver that will proxy to WSGI server running a flask
application. This setup guide uses gunicorn as the WSGI server and nginx as we
webserver, but you can easily search around for alternatives. This same
setup should work with any virtual machine setup with your favorite
cloud provider, but I followed these procedures to host the application
on a Raspberry Pi running Raspbian 10. Most of the examples will
draw specifically from my setup, but should be easy to adapt to your
environment.


Pre-requisites
^^^^^^^^^^^^^^
To follow along with the rest of the guide, you'll need the following
packages installed on your distribution:

* Python >= 3.9
* Nginx >= 1.x
* Gunicorn >= 20.1.x - Note that this will not get installed with
  requirements.txt because the MedOps app does not actually depend
  on it. It's an external service that is part of the hosting
  environment decision.


Setting Up the Project
^^^^^^^^^^^^^^^^^^^^^^
The MedOps source tree can be used as to host the provided Flask application.
Depending on your preference, you can install all the python dependencies into a
virtualenv or into the base installation on your system. In my setup, I run
multiple applications from the same server, so I opted for using a virtualenv.
The directory structure I have set up (though the names are slightly different)
is:

.. code-block:: text

    /var/www/application/
        api/ <--- This is a git clone of the cod repository

This is mainly because I hosted the docs first in the root of
:code:`/var/www/application` and didn't want to break the site to
reorganizing the folder structure.

Within the virutalenv, I ran the following commands to install the python
requirements:

1. :code:`python -m pip install -r requirements.txt`
2. :code:`python -m pip install gunicorn`

If everything is set up correctly so far, running :code:`pytest` from the code
directory should yield passing tests.


Gunicorn Setup
^^^^^^^^^^^^^^
Before we can set up the webserver to proxy our flask application, the flask
application needs to be running. There is a systemd service file included in
the repository under :code:`config/guniforn.service`. Make sure to update
the paths to match your environment.

You may need to figure out where custom systemd service files should be installed
on your system, but a common place is :code:`/etc/systemd/system`. After the
gunicorn service file is in place:

* To enable the serve to be managed automatically on bootup: `sudo systemctl enable gunicorn.service`
* To start the application now: `sudo systemctl start gunicorn.service`
* Check that your application is running: `sudo systemctl status gunicorn.service`


Nginx Config
^^^^^^^^^^^^
Once the flask app is up and running locally, its time to proxy it through nginx. And example Nginx
configuration is in :code:`configs/nginx`. Again, make sure to update the paths, including the location
directives to match the environment you have and update the :code:`server_name` if applicable.

The nginx configuration should be placed in: :code:`/etc/nginx/sites-available` and linked into
:code:`/etc/nginx/sites-enabled` when you're ready to host it.

Once linked into the enabled sites folder, test ngninx wont choke using :code:`sudo nginx -t`. When
it's ready to run, reload nginx: :code:`sudo /etc/init.d/nginx reload`.
