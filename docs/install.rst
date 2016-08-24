Installation
============

In this guide I use Debian for example setup. Supporting for Red Hat will be added later.

Environment Setup
-----------------

1. Add new user and prepare the locations for DanceCat:

.. code-block:: bash

   useradd dancecat

   sudo mkdir -p /opt/dancecat
   sudo chown dancecat.dancecat /opt/dancecat

   sudo mkdir -p /etc/dancecat
   sudo chown dancecat.dancecat /etc/dancecat

   sudo mkdir -p /var/run/dancecat
   sudo chown dancecat.dancecat /var/run/dancecat

   sudo mkdir -p /var/log/dancecat
   sudo chown dancecat.dancecat /var/log/dancecat

2. Install git:

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

   cd /var/run/dancecat
   virtualenv venv

5. Install necessary modules for your Python virtual environment:

Install packages which will be used to install Python modules:

.. code-block:: bash

   sudo apt-get install build-essential autoconf libtool
   sudo apt-get install libpq-dev python-dev

Install Python modules:

.. code-block:: bash

   su - dancecat

   source /var/run/dancecat/venv/bin/activate
   pip install --upgrade setuptools
   pip install --upgrade pip
   pip install -r /opt/dancecat/requirements.txt

Download and install `mysql-connector-python <https://dev.mysql.com/downloads/connector/python/>`_.
My version is 2.1.3.

.. code-block:: bash

   su - dancecat

   source /var/run/dancecat/venv/bin/activate

   tar zvfx mysql-connector-python-2.1.3.tar.gz
   cd mysql-connector-python-2.1.3
   python setup.py install

6. Run for a simple test:

.. code-block:: bash

   su - dancecat

   cd /opt/dancecat
   mkdir var

   source /var/run/dancecat/venv/bin/activate
   export PYTHONPATH=`pwd`:$PYTHONPATH
   py.test tests

If the test work well then you are ready for the next step: `Config <install.html#config-dancecat>`_.
You can setup *dancecat* user *.bashrc* file for later convenience.
Later in this document I will assume that you are already in the right environment.

7. Edit .bashrc

.. code-block:: bash

   su - dancecat

   echo "export PYTHONPATH=/opt/dancecat" >> ~/.bashrc
   echo "source /var/run/dancecat/venv/bin/activate" >> ~/.bashrc


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


Init Database
-------------

.. code-block:: bash

   su - dancecat

   cd /opt/dancecat

   export CONFIG_FILE=/etc/dancecat/config.cfg
   python DanceCat/Console db_create_all


Migrate Database
----------------

1. Upgrade database to new version of DanceCat:

.. code-block:: bash

   su - dancecat
   cd /opt/dancecat

   export CONFIG_FILE=/etc/dancecat/config.cfg
   python DanceCat/Console db upgrade

2. Downgrade database to previous version:

.. code-block:: bash

   su - dancecat
   cd /opt/dancecat

   export CONFIG_FILE=/etc/dancecat/config.cfg
   python DanceCat/Console db downgrade
