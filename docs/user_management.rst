User Management
===============

Add user to the system
----------------------

To be able to use DanceCat, firstly user must have been allowed by administrators.
Follow that concept, user's emails must exist in **allowed_user** table before they can
process any further step. There is one console command allow you adding those email
to that that table.

.. code-block:: bash

   su - dancecat

   cd /opt/dancecat
   export CONFIG_FILE=/etc/dancecat/config.cfg
   python DanceCat/Console add_allowed_user example@localdomain.com

Sign Up and Log In
------------------

Following the above step, allowed users can now Sign Up new account on DanceCat.
For convenience, *Sign Up* and *Log In* using the same page. Just go to your DanceCat site,
enter user email and password to *Log In* form, press **Log In** button to sign up.

Wonderful! Now you can start using DanceCat. Follow `next step <connection_management.html>`_
to manage your connections.
