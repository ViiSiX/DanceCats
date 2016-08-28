Installation
============

In this guide I use Debian for example setup. Supporting for Red Hat
based OS will be added later.

Environment Setup
-----------------

1. Add new user and prepare the locations for DanceCat:

.. code-block:: bash

   sudo useradd dancecat

   sudo mkdir -p /opt/dancecat
   sudo chown dancecat.dancecat /opt/dancecat

   sudo mkdir -p /etc/dancecat
   sudo chown dancecat.dancecat /etc/dancecat

   sudo mkdir -p /var/run/dancecat
   sudo chown dancecat.dancecat /var/run/dancecat

   sudo mkdir -p /var/log/dancecat
   sudo chown dancecat.dancecat /var/log/dancecat

2. Install packages which will be used later

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

Git to pull and deploy codes:

.. code-block:: bash

   sudo apt-get install git

3. Pull the code from `DanceCat's repository <https://github.com/scattm/DanceCat>`_.

.. code-block:: bash

   su - dancecat

   cd /opt
   git clone https://github.com/scattm/DanceCat.git dancecat

4. Install necessary packages to setup a virtual environment for Python.
If you already done this, please skip to step 5.

.. code-block:: bash

   sudo apt-get install python-virtualenv

   su - dancecat

   cd ~
   virtualenv venv

5. Install necessary modules for your Python virtual environment:

Install Python modules:

.. code-block:: bash

   su - dancecat

   source ~/venv/bin/activate
   pip install --upgrade setuptools
   pip install --upgrade pip
   pip install -r /opt/dancecat/requirements.txt

6. Run for a simple test:

.. code-block:: bash

   su - dancecat

   cd /opt/dancecat
   mkdir var

   source ~/venv/bin/activate
   export PYTHONPATH=`pwd`:$PYTHONPATH
   py.test tests

If the test work well then you are ready for the next step: `Config <install.html#config-dancecat>`_.
You can setup *dancecat* user *.bashrc* file for later convenience.
Later in this document I will assume that you are already in the right environment.

7. Packing client's codes:

.. code-block:: bash

   su - dancecat

   cd /opt/dancecat

   npm install

   node node_modules/webpack/bin/webpack.js


8. Edit .bashrc

.. code-block:: bash

   su - dancecat

   echo "export PYTHONPATH=/opt/dancecat" >> ~/.bashrc
   echo "source ~/venv/bin/activate" >> ~/.bashrc


Config DanceCat
---------------

Copy and edit configuration file:

.. code-block:: bash

   su - dancecat

   cd /etc/dancecat
   cp /opt/dancecat/config.cfg.dist ./config.cfg

Example configuration file's content:

.. code-block:: none

   WTF_CSRF_ENABLED = True
   SECRET_KEY = 'dance cat is dancing'

   DB_ENCRYPT_KEY = 'dance cat is trying to dance'
   DB_TIMEOUT = 120

   FREQUENCY_PID = '/var/run/dancecat/frequency.pid'

   QUERY_TEST_LIMIT = 100

   JOB_RESULT_VALID_SECONDS = 86400

   SQLALCHEMY_DATABASE_URI = 'sqlite:////var/run/dancecat/dancecat.db'
   SQLALCHEMY_TRACK_MODIFICATIONS = False

   REDISLITE_PATH = '/var/run/dancecat/dancecat.rdb'
   REDISLITE_WORKER_PID = '/var/run/dancecat/rlworker.pid'

   MAIL_SERVER = 'localhost'
   MAIL_PORT = 465

**Explain DanceCat's config attribute**

*DB_ENCRYPT_KEY* Key which is used to encrypt connections credentials.

*DB_TIMEOUT* Default timeout for queries to run on a database connection.

*QUERY_TEST_LIMIT* Timeout for a connection to be tested.

*FREQUENCY_PID* Location for schedule worker PID file.

*JOB_RESULT_VALID_SECONDS* Time for a job's result to remain available.

*REDISLITE_PATH* Location for RedisLite database file.

*REDISLITE_WORKER_PID* Location for RedisLite worker PID file.

Other configuration: Please check on *Flask* and its extensions for further information.


Setup Database
--------------

There are 2 ways to setup database: create full database schema or migrate using
generated migration scripts.

1. Create full database schema

Using this methods, you will able to fully deploy DanceCat schema to your database with
less bugs compare to the later method. However, for later upgrade, you must update your
schema by yourself.

.. code-block:: bash

   su - dancecat

   cd /opt/dancecat

   export CONFIG_FILE=/etc/dancecat/config.cfg
   python DanceCat/Console db_create_all

2. Migrate your database schema using generated scripts

Using this method, you don't have to worry about updating your database schema to keep up
with releases, but be careful because you may encounter bugs on some RDBMS like SQLite3.

.. code-block:: bash

   su - dancecat
   cd /opt/dancecat

   export CONFIG_FILE=/etc/dancecat/config.cfg

   # Upgrading
   python DanceCat/Console db upgrade

   # Downgrading
   python DanceCat/Console db downgrade


Bootstrap and Run
-----------------

Copy the example Bootstrap file and edit it to suit yourself.

.. code-block:: bash

   su - dancecat
   cd /opt/dancecat

   cp DanceCatBootstrap.py.dist DanceCatBootstrap.py

You don't really have to edit much. Here is the example for you:

.. code-block:: python

   """
   Running script for DanceCat
   """
   import os
   # Just in case proxy server do not work.
   from werkzeug.contrib.fixers import ProxyFix
   from DanceCat import app, socket_io, rdb, \
       Views, ErrorViews, Socket, FrequencyTaskChecker

   # In case of `code 400, message Bad request`
   os.putenv('LANG', 'en_US.UTF-8')
   os.putenv('LC_ALL', 'en_US.UTF-8')

   # Just in case proxy server do not work.
   app.wsgi_app = ProxyFix(app.wsgi_app)

   FrequencyTaskChecker.start(60, app.config.get('FREQUENCY_PID', 'frequency.pid'))

   with app.app_context():
       rdb.start_worker()

   # Remove the following block if you use gunicorn.
   socket_io.run(app,
                 host='0.0.0.0',
                 port=8443,
                 )

Run it:

.. code-block:: bash

   su - dancecat

   cd /opt/dancecat
   export CONFIG_FILE=/etc/dancecat/config.cfg
   python DanceCatBootstrap.py

Go to your browser and start using DanceCat.

Using with Nginx and WSGI
-------------------------

For this guide, I will use Gunicorn as WSGI web server and Nginx as a proxy server
to public DanceCat.

1. Install Nginx

.. code-block:: bash

   sudo apt-get install nginx

2. Install Gunicorn

.. code-block:: bash

   su - dancecat

   pip install gunicorn

3. Create a script to start the app with gunicorn

.. code-block:: bash

   su - dancecat

   vim /opt/dancecat/start.sh

.. code-block:: bash

   #!/bin/bash

   export CONFIG_FILE=/etc/dancecat/config.cfg

   # Please change log level to one that suite your environment.
   gunicorn --worker-class eventlet \
     -w 1 DanceCatBootstrap:app \
     -p /var/run/dancecat/dancecat.pid \
     -D --bind unix:/var/run/dancecat/dancecat.sock \
     --log-file /var/log/dancecat/dancecat.log \
     --log-level debug \
     --timeout=90 \
     --graceful-timeout=10 -m 007

.. code-block:: bash

   chmod u+x /opt/dancecat/start.sh

4. Edit your `DanceCatBootstrap.py <install.html#bootstrap-and-run>`_, remove the
following lines since gunicorn will run it for you.

.. code-block:: python

   socket_io.run(app,
                 host='0.0.0.0',
                 port=8443,
                 )

5. Start your application

.. code-block:: bash

   su - dancecat

   /opt/dancecat/start.sh

6. Config Nginx

Create a config file that allow Nginx to act as a proxy to publish your DanceCat:

.. code-block:: bash

   sudo vim /etc/nginx/site-available/dancecat.localdomain.conf

.. code-block:: none

   server {
     listen       80;
     server_name  dancecat.localdomain;

     access_log /var/log/nginx/dancecat.localdomain_access.log main;
     error_log  /var/log/nginx/dancecat.localdomain_error.log;

     location / {
       proxy_pass http://unix:/var/run/dancecat/dancecat.sock;

       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
     }

     location /socket.io {
       proxy_pass       http://unix:/var/run/dancecat/dancecat.sock;
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

Go to your browser and start using DanceCat.

Security
--------

Since DanceCat allows users to query again databases, you may be want to consider
what permissions on your databases should be given to DanceCat before you public it.
You should also limit network access to DanceCat server and enable other security methods
that you have, ex "iptables", "SELinux" and enable SSL on your site.
