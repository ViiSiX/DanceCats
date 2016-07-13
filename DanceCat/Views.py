"""
Docstring for DanceCat.Views module.

This module contains functions which will be called
whenever the application receive the right url request.
"""

import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
import flask_excel as excel
from DanceCat import app, db, lm, rdb
from DanceCat.Models import User, AllowedEmail, Connection, \
    QueryDataJob, TrackJobRun, JobMailTo, Job
from DanceCat.Forms import RegisterForm, ConnectionForm, QueryJobForm
from DanceCat.DatabaseConnector import DatabaseConnector, DatabaseConnectorException
from .JobWorker import job_worker
from . import Helpers
from . import Constants


@lm.user_loader
def load_user(user_id):
    """Load the user."""
    return User.query.get(user_id)


@app.route('/')
def index():
    """Render and return About Page."""
    return render_template('about.html',
                           title=Constants.PROJECT_NAME)


@app.route('/job')
@login_required
def job():
    """Render and return Job Listing Page."""
    jobs = QueryDataJob.query.all()
    job_lists = []
    for job_object in jobs:
        job_lists.append({
            'id': job_object.id,
            'name': job_object.name,
            'last_updated': job_object.lastUpdated,
            'user_email': job_object.User.email,
            'connection_name': job_object.Connection.name
        })
    return render_template('query_job/list.html',
                           title=Constants.PROJECT_NAME,
                           jobs=job_lists,
                           trigger_url=url_for('job_run'))


@app.route('/job/create', methods=['GET', 'POST'])
def job_create():
    """Render and return Create New Job Page."""
    form = QueryJobForm(request.form)
    form.connectionId.choices = \
        Connection.query.with_entities(Connection.id, Connection.name).all()

    if request.method == 'POST':
        if request.form.has_key('add-email'):
            form.emails.append_entry()

        elif form.validate_on_submit():
            new_job = QueryDataJob(name=request.form['name'],
                                   annotation=request.form['annotation'],
                                   connection_id=request.form['connectionId'],
                                   query_string=request.form['queryString'],
                                   user_id=current_user.id)
            db.session.add(new_job)
            db.session.commit()

            for mail_to in form.emails.entries:
                if mail_to.data != '':
                    new_mail_to = JobMailTo(
                        job_id=new_job.id,
                        email_address=mail_to.data
                    )
                    db.session.add(new_mail_to)
                    db.session.commit()

            return redirect(url_for('job'))
    return render_template('query_job/form.html',
                           title=Constants.PROJECT_NAME,
                           action='Creating',
                           action_url=url_for('job_create'),
                           form=form)


@app.route('/job/edit/<job_id>', methods=['GET', 'POST'])
@login_required
def job_edit(job_id):
    """Render and return Edit Job Page."""
    editing_job = QueryDataJob.query.get_or_404(job_id)
    form = QueryJobForm(request.form, editing_job)
    form.connectionId.choices = \
        Connection.query.with_entities(Connection.id, Connection.name).all()
    if len(form.emails.entries) == 0:
        form.emails.append_entry()
    if request.method == 'POST':
        if request.form.has_key('add-email'):
            form.emails.append_entry()

        elif form.validate_on_submit():
            form.populate_obj(editing_job)
            db.session.commit()

            db.session.query(JobMailTo). \
                filter_by(jobId=editing_job.id). \
                update({JobMailTo.enable: False})
            db.session.commit()
            for mail_to in form.emails.entries:
                if mail_to.data != '':
                    existing_mail_to = \
                        JobMailTo.query.filter_by(
                            jobId=editing_job.id, emailAddress=mail_to.data
                        ).first()
                    if existing_mail_to is None:
                        new_mail_to = JobMailTo(
                            job_id=editing_job.id,
                            email_address=mail_to.data
                        )
                        db.session.add(new_mail_to)
                        db.session.commit()
                    else:
                        existing_mail_to.enable = True
                        db.session.commit()

            return redirect(url_for('job'))

    return render_template('query_job/form.html',
                           title=Constants.PROJECT_NAME,
                           action='Edit',
                           action_url=url_for('job_edit', job_id=job_id),
                           form=form)


@app.route('/job/delete', methods=['POST'])
@login_required
def job_delete():
    """Delete a Job."""
    deleting_job = Job.query.get(request.form['id'])
    if deleting_job is not None:
        db.session.delete(deleting_job)
        db.session.commit()

        return jsonify({
            'deleted': True
        })

    return jsonify({
        'deleted': False
    })


@app.route('/job/run', methods=['POST'])
@login_required
def job_run():
    """Trigger a job."""
    triggered_job = QueryDataJob.query.get_or_404(request.form['id'])
    tracker = TrackJobRun(triggered_job.id)
    db.session.add(tracker)
    db.session.commit()
    queue = rdb.queue
    queue.enqueue(
        f=job_worker, kwargs={
            'job_id': triggered_job.id,
            'tracker_id': tracker.id
        },
        ttl=900,
        result_ttl=app.config.get('JOB_RESULT_VALID_SECONDS', 86400),
        job_id="%d" % tracker.id
    )
    return jsonify({'ack': True, 'tracker_id': tracker.id})


@app.route('/job/result/<tracker_id>/<result_type>')
@login_required
def job_result(tracker_id, result_type):
    """Download Job's result."""
    queue = rdb.queue
    result = queue.fetch_job(tracker_id).result
    if result_type in ['csv', 'xls', 'xlsx', 'ods']:
        result_array = [list(result['header'])]
        for row in result['rows']:
            result_array.append(list(row))
        return excel.make_response_from_array(
            result_array,
            result_type,
            file_name="Result_tid_{tid}.{ext}".format(
                tid=tracker_id,
                ext=result_type
            )
        )
    elif result_type == 'raw':
        return jsonify(result)
    else:
        abort(404)


@app.route('/job/latest-result/<job_id>/<result_type>')
@login_required
def job_latest_result(job_id, result_type):
    """Download Job's latest result."""
    fetching_result_job = Job.query.get_or_404(job_id)
    last_tracker = TrackJobRun.query.filter_by(jobId=fetching_result_job.id).\
        order_by(TrackJobRun.ranOn.desc()).first()
    if last_tracker is not None:
        queue = rdb.queue
        result = queue.fetch_job(str(last_tracker.id)).result
        if result_type in ['csv', 'xls', 'xlsx', 'ods']:
            result_array = [list(result['header'])]
            for row in result['rows']:
                result_array.append(list(row))
            return excel.make_response_from_array(
                result_array,
                result_type,
                file_name="Result_tid_{tid}.{ext}".format(
                    tid=last_tracker.id,
                    ext=result_type
                )
            )
        elif result_type == 'raw':
            return jsonify(result)

    abort(404)


@app.route('/connection')
@login_required
def connection():
    """Render and return Collection Listing Page."""
    connections = Connection.query.all()
    connections_list = []
    for connection_obj in connections:
        connection_type = Constants.CONNECTION_TYPES_DICT[connection_obj.type]['name']
        if not connection_type:
            connection_type = 'Others'
        connections_list.append({
            'id': connection_obj.id,
            'name': connection_obj.name,
            'type': connection_type,
            'host': connection_obj.host,
            'database': connection_obj.database
        })
    return render_template('connection/list.html',
                           title=Constants.PROJECT_NAME,
                           connections=connections_list)


@app.route('/connection/create', methods=['GET', 'POST'])
@login_required
def connection_create():
    """Render and return Create New Connection Page."""
    form = ConnectionForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_connection = Connection(name=request.form['name'],
                                        db_type=int(request.form['type']),
                                        database=request.form['database'],
                                        host=request.form['host'],
                                        port=Helpers.null_handler(request.form['port']),
                                        user_name=request.form['userName'],
                                        password=Helpers.null_handler(request.form['password']),
                                        creator_user_id=current_user.id
                                        )
            db.session.add(new_connection)
            db.session.commit()
            return redirect(url_for('connection'))
    return render_template('connection/form.html',
                           title=Constants.PROJECT_NAME,
                           action='Create',
                           action_url=url_for('connection_create'),
                           test_url=url_for('connection_test'),
                           form=form)


@app.route('/connection/edit/<connection_id>', methods=['GET', 'POST'])
@login_required
def connection_edit(connection_id):
    """Render and return Edit Connection Page."""
    editing_connection = Connection.query.get_or_404(connection_id)
    form = ConnectionForm(request.form, editing_connection)
    if request.method == 'GET':
        return render_template('connection/form.html',
                               title=Constants.PROJECT_NAME,
                               action='Edit',
                               action_url=url_for('connection_edit', connection_id=connection_id),
                               test_url=url_for('connection_test', connection_id=connection_id),
                               form=form)
    else:
        if form.validate_on_submit():
            if Helpers.null_handler(request.form['password']) is not None:
                form.populate_obj(editing_connection)
                editing_connection.encrypt_password(request.form['password'])
            else:
                old_password = editing_connection.password
                form.populate_obj(editing_connection)
                editing_connection.password = old_password
            db.session.commit()
        return redirect(url_for('connection'))


@app.route('/connection/delete', methods=['POST'])
@login_required
def connection_delete():
    """Delete the Connection."""
    deleting_connection = Connection.query.get(request.form['id'])
    if deleting_connection is not None:
        db.session.delete(deleting_connection)
        db.session.commit()

        return jsonify({
            'deleted': True
        })
    else:
        return jsonify({
            'deleted': False
        })


@app.route('/connection/get_mime/', defaults={'connection_id': 0})
@app.route('/connection/get_mime/<connection_id>')
@login_required
def connection_get_mime(connection_id):
    """Get the mime of the Connection. Currently unused."""
    conn = Connection.query. \
        with_entities(Connection.id,
                      Connection.type
                      ).filter_by(id=connection_id).first()
    if conn is not None:
        return jsonify({
            'id': connection_id,
            'mime': Constants.CONNECTION_TYPES_DICT[conn[1]]['mime']
        })
    else:
        return jsonify({
            'id': 0
        }), 404


@app.route('/connection/test', methods=['POST'], defaults={'connection_id': 0})
@app.route('/connection/test/<connection_id>', methods=['POST'])
@login_required
def connection_test(connection_id):
    """Test the connection."""
    form = ConnectionForm(obj=request.form)
    if form.validate_on_submit():
        if connection_id == 0:
            new_connection = Connection(name=request.form['name'],
                                        db_type=int(request.form['type']),
                                        database=request.form['database'],
                                        host=request.form['host'],
                                        port=Helpers.null_handler(request.form['port']),
                                        user_name=request.form['userName'],
                                        password=Helpers.null_handler(request.form['password']),
                                        creator_user_id=current_user.id
                                        )
            testing_config = new_connection.db_config_generator()
        else:
            testing_connection = Connection.query.get(connection_id)
            if Helpers.null_handler(request.form['password']) is not None:
                form.populate_obj(testing_connection)
                testing_connection.encrypt_password(request.form['password'])
            else:
                old_password = testing_connection.password
                form.populate_obj(testing_connection)
                testing_connection.password = old_password
            testing_config = testing_connection.db_config_generator()

        db_connect = DatabaseConnector(int(request.form['type']), testing_config)
        try:
            db_connect.connection_test(10)
            return jsonify({
                'connected': True
            })
        except DatabaseConnectorException:
            return jsonify({
                'connected': False
            })

    return jsonify({
        'connected': False
    })


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log In Page."""
    form = RegisterForm(request.form)
    if request.method == 'GET':
        return render_template('login.html',
                               title=Constants.PROJECT_NAME,
                               form=form)
    if form.validate_on_submit():
        user_email = request.form['email']
        user_password = request.form['password']
        registered_user = User.query.filter_by(email=user_email).first()
        if registered_user is None:
            allowed_email = AllowedEmail.query.filter_by(email=user_email).first()
            if allowed_email is None:
                flash('You are not allowed to use this site!', 'alert-danger')
                return redirect(url_for('login'))
            else:
                new_user = User(user_email=user_email,
                                user_password=user_password)
                db.session.add(new_user)
                db.session.commit()
                flash('You have been register as new user! Please login again!', 'alert-info')
                return redirect(url_for('login'))
        else:
            if Helpers.check_password(registered_user.password, user_password):
                login_user(registered_user)
                registered_user.lastLogin = datetime.datetime.now()
                db.session.commit()
                flash('You have been logged in successfully!', 'alert-success')
                return redirect(request.args.get('next') or url_for('job'))
            else:
                flash('Wrong password!', 'alert-danger')
                return redirect(url_for('login'))


@app.route('/logout')
def logout():
    """Log Out."""
    logout_user()
    return redirect(url_for('index'))
