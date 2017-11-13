Installation
============

In this guide we use Debian for example setup. Supporting for Red Hat
based OS will be added later.

Environment Setup
-----------------

We will go through the following steps to set up the right environment for DanceCats.
The application need Python to run and Node.js to package front-end code. To prevent any conflict
on the system, we will use a Python virtual environment with latest installation modules
and a dedicated system user. Also install required develop packages if
your system have not had them yet as we will need them to build some modules on your
Python virtual environment.

1. Add new user *dancecats* for DanceCats and prepare the necessary locations for DanceCats
which also belong to *dancecats* user.

.. code-block:: bash

   sudo useradd dancecats

   sudo mkdir -p /opt/dancecats
   sudo chown dancecats.dancecats /opt/dancecats

   sudo mkdir -p /etc/dancecats
   sudo chown dancecats.dancecats /etc/dancecats

   sudo mkdir -p /var/run/dancecats
   sudo chown dancecats.dancecats /var/run/dancecats

   sudo mkdir -p /var/log/dancecats
   sudo chown dancecats.dancecats /var/log/dancecats

2. Install packages which will be used to build and setup DanceCats

Build essential used for install Python's modules:

.. code-block:: bash

   sudo apt-get install build-essential autoconf libtool
   sudo apt-get install libpq-dev python-dev

`Node.js <https://nodejs.org/en/download/package-manager/>`_ for packing client's scripts:

.. code-block:: bash

   # Run this if your system does not have curl
   sudo apt-get install curl

   curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
   sudo apt-get install -y nodejs

Install *git* which will be used for cloning source code and upgrade your DanceCats.

.. code-block:: bash

   sudo apt-get install git

3. Pull the code from `DanceCats' repository <https://github.com/ViiSiX/DanceCats>`_

.. code-block:: bash

   su - dancecat

   cd /opt
   git clone https://github.com/ViiSiX/DanceCats.git dancecats

4. Install necessary packages to setup a virtual environment for Python

*If you already done this, please skip to step 5.*

Virtual environment will create a directory which contains all the Python's necessary
executables to run DanceCats while does not make any change to your system's Python modules.

.. code-block:: bash

   sudo apt-get install python-virtualenv

   su - dancecats

   cd ~
   virtualenv venv

5. Install necessary modules on your Python virtual environment

Latest *pip*, *wheel* and *setuptools* are required, you need to upgrade them
in case your system's Python is having the old ones. All other required modules
are listed in *requirements.txt*.

.. code-block:: bash

   su - dancecats

   source ~/venv/bin/activate
   pip install --upgrade setuptools
   pip install --upgrade pip
   pip install --upgrade wheel
   pip install -r /opt/dancecats/requirements.txt

6. Run a simple test to test you environment

.. code-block:: bash

   su - dancecats

   cd /opt/dancecats

   source ~/venv/bin/activate
   export PYTHONPATH=`pwd`:$PYTHONPATH
   py.test tests

If the test work well then you are ready for the next step: `Config <install.html#config-dancecat>`_.

7. Packing client's codes

Client's codes include CSS and Javascript files in *client* directory and their dependencies
will be installed by *npm*. By doing this step, the Node.js *webpack* module will pack and
put those code in *DanceCats/static/bundle* directory which will be publish to clients' browsers.

.. code-block:: bash

   su - dancecats

   cd /opt/dancecats

   npm install

   node node_modules/webpack/bin/webpack.js


8. Edit .bashrc

Set up *dancecats* user's *.bashrc* file will give you later convenience. Beside running
the application, you have to switch to DanceCats' Python's virtual environment
every time you use console command or testing the package.

Later in this document we will assume that you have already done this step.

.. code-block:: bash

   su - dancecats

   echo "source ~/venv/bin/activate" >> ~/.bashrc


Config DanceCats
---------------

Copy and edit configuration file:

.. code-block:: bash

   su - dancecats

   cp /opt/dancecats/config.cfg.dist /etc/dancecats/config.cfg

Example configuration file's content:

.. code-block:: none

   WTF_CSRF_ENABLED = True
   SECRET_KEY = 'dancecat is dancing'

   DB_ENCRYPT_KEY = 'dancecat is trying to dance'
   DB_TIMEOUT = 120

   FREQUENCY_PID = '/var/run/dancecats/frequency.pid'
   FREQUENCY_INTERVAL_SECONDS = 60

   QUERY_TEST_LIMIT = 100

   JOB_RESULT_VALID_SECONDS = 86400
   JOB_WORKER_EXECUTE_TIMEOUT = 3600
   JOB_WORKER_ENQUEUE_TIMEOUT = 1800

   SQLALCHEMY_DATABASE_URI = 'sqlite:////var/run/dancecats/dancecats.db'
   SQLALCHEMY_TRACK_MODIFICATIONS = False

   REDISLITE_PATH = '/var/run/dancecats/dancecats.rdb'
   REDISLITE_WORKER_PID = '/var/run/dancecats/rlworker.pid'

   MAIL_SERVER = 'localhost'
   MAIL_PORT = 465

**Explain DanceCats' config attribute**

*DB_ENCRYPT_KEY* Key which is used to encrypt connections credentials.

*DB_TIMEOUT* Default timeout for queries to run on a database connection.

*QUERY_TEST_LIMIT* Timeout for a connection to be tested.

*FREQUENCY_PID* Location for schedule worker PID file.

*FREQUENCY_INTERVAL_SECONDS* Interval in seconds for frequency task checker to re-check the schedules.

*JOB_RESULT_VALID_SECONDS* Time for a job's result to remain available.

*JOB_WORKER_EXECUTE_TIMEOUT* Timeout in seconds for a job to execute.

*JOB_WORKER_ENQUEUE_TIMEOUT* Time for a job to live waiting in the queue.

*REDISLITE_PATH* Location for RedisLite database file.

*REDISLITE_WORKER_PID* Location for RedisLite worker PID file.

Other configuration: Please check on *Flask* and its extensions for further information.


Setup Database
--------------

DanceCats stores and manages it data on RDBMS via `SQLAlchemy <http://www.sqlalchemy.org/>`_.
Basically you can run it on whatever RDBMS that SQLAlchemy supports,
although we have just tested it with SQLite, MySQL and PostgreSQL.
Please feel free to try others and let us know if they work or not.

To config your DanceCats database, set the value of *SQLALCHEMY_DATABASE_URI*
in */etc/dancecats/config.cfg* file to the right connection string. You can
follow the example of connection strings `here <http://docs.sqlalchemy.org/en/latest/core/engines.html>`_.

After set up the connection string, you need to set up the database schema.
There are 2 ways to do that: create full database schema or migrate using
generated migration scripts.

1. Create full database schema

Using this methods, you will able to fully deploy DanceCats schema to your database with
less bugs compare to the later method. However, for later upgrade, you must update your
schema by yourself.

.. code-block:: bash

   su - dancecats

   cd /opt/dancecats

   export CONFIG_FILE=/etc/dancecats/config.cfg
   python -m DanceCats.Console db_create_all

2. Migrate your database schema using generated scripts

Using this method, you don't have to worry about updating your database schema to keep up
with releases, but be careful because you may encounter bugs on some RDBMS like SQLite.

.. code-block:: bash

   su - dancecats
   cd /opt/dancecats

   export CONFIG_FILE=/etc/dancecats/config.cfg

   # Upgrading
   python -m DanceCats.Console db upgrade

   # Downgrading
   python -m DanceCats.Console db downgrade

**Note:** Please upgrade your database schema whenever you upgrade DanceCats to new version.


Bootstrap and Run
-----------------

Copy the example Bootstrap file and edit it to suit yourself.

.. code-block:: bash

   su - dancecats
   cd /opt/dancecats

   cp DanceCatsBootstrap.py.dist DanceCatsBootstrap.py

You don't really have to edit much. Here is the example for you:

.. code-block:: python

   """
   Running script for DanceCats
   """
   import os
   # Just in case proxy server do not work.
   from werkzeug.contrib.fixers import ProxyFix
   from DanceCats import app, socket_io, rdb, \
       Views, ErrorViews, Socket, FrequencyTaskChecker

   # In case of `code 400, message Bad request`
   os.putenv('LANG', 'en_US.UTF-8')
   os.putenv('LC_ALL', 'en_US.UTF-8')

   # Just in case proxy server do not work.
   app.wsgi_app = ProxyFix(app.wsgi_app)

   FrequencyTaskChecker.start(
       interval=app.config.get('FREQUENCY_INTERVAL_SECONDS', 60),
       pid_path=app.config.get('FREQUENCY_PID', 'frequency.pid')
   )

   with app.app_context():
       rdb.start_worker()

   # Remove the following block if you use gunicorn.
   socket_io.run(app,
                 host='0.0.0.0',
                 port=8080,
                 )

Run it:

.. code-block:: bash

   su - dancecats

   cd /opt/dancecats
   export CONFIG_FILE=/etc/dancecats/config.cfg
   python DanceCatsBootstrap.py

Go to your browser and start using DanceCats on port 8080. Example http://localhost:8080

Using with Nginx and WSGI
-------------------------

For this guide, we will use Gunicorn as WSGI web server and Nginx as a proxy server
to public DanceCats.

1. Install Nginx

.. code-block:: bash

   sudo apt-get install nginx

2. Install Gunicorn

.. code-block:: bash

   su - dancecats

   pip install gunicorn

3. Create a script to start the app with gunicorn

.. code-block:: bash

   su - dancecats

   vim /opt/dancecats/start.sh

.. code-block:: bash

   #!/bin/bash

   export CONFIG_FILE=/etc/dancecats/config.cfg

   # Please change log level to one that suite your environment.
   gunicorn --worker-class eventlet \
     -w 1 DanceCatsBootstrap:app \
     -p /var/run/dancecats/dancecats.pid \
     -D --bind unix:/var/run/dancecats/dancecats.sock \
     --log-file /var/log/dancecats/dancecats.log \
     --log-level debug \
     --timeout=90 \
     --graceful-timeout=10 -m 007

.. code-block:: bash

   chmod u+x /opt/dancecats/start.sh

4. Edit your `DanceCatsBootstrap.py <install.html#bootstrap-and-run>`_, remove the
following lines since gunicorn will run it for you.

.. code-block:: python

   socket_io.run(app,
                 host='0.0.0.0',
                 port=8443,
                 )

5. Start your application

.. code-block:: bash

   su - dancecats

   /opt/dancecats/start.sh

6. Config Nginx

Create a config file that allow Nginx to act as a proxy to publish your DanceCats:

.. code-block:: bash

   sudo vim /etc/nginx/site-available/dancecats.localdomain.conf

.. code-block:: none

   server {
     listen       80;
     server_name  dancecats.localdomain;

     access_log /var/log/nginx/dancecats.localdomain_access.log main;
     error_log  /var/log/nginx/dancecats.localdomain_error.log;

     location / {
       proxy_pass http://unix:/var/run/dancecats/dancecats.sock;

       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
     }

     location /socket.io {
       proxy_pass       http://unix:/var/run/dancecats/dancecats.sock;
       proxy_buffering  off;

       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;

       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection "Upgrade";
     }
   }

Restart Nginx

.. code-block:: bash

   sudo service nginx configtest

   sudo service nginx restart

Go to your browser and start using DanceCats. Ex: http://dancecats.your-domain.com

Security
--------

Since DanceCats allows users to query against databases, you may be want to consider
what permissions on your databases should be given to DanceCats before you public it.
You should also limit network access to DanceCats server and enable other security methods
that you have, ex "iptables", "SELinux" and enable SSL on your site.
