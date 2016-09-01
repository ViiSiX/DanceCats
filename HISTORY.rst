0.1.2 - Documentation (cont) and Fix Bug
----------------------------------------

*Date: Aug 31, 2016*

**Change:**

- Add console command to `add allowed user <user_management.html#add-user-to-the-system>`_.
- Document for WSGI and Nginx
- User Manual

**Fixed bugs:**

- Critical error after delete connections that having jobs
- Corrupted results of jobs when mailing failed

0.1.1 - Documentation and Feature Improvement
---------------------------------------------

*Date: Aug 25, 2016*

**Changes:**

- Support timeout option for each job.
- Test on Helpers function.
- Logical delete schedule and job.
- Add console commands to migrate database and update missed schedule.
- Add document by Sphinx.
- PostgreSQL support.

**Fixed bugs:**

- Missing first part of migrating.
- Missing schedule id in track table.


0.1.0 - The very first release
------------------------------

*Date: Aug 2, 2016*

**Changes:**

- Create, edit, test and delete connections.
- Create, edit and delete database query jobs.
- Support MySQL and SQL Server.
- Database query job run on background and storing using Redis-lite.
- Send results via email.
- Job scheduling.