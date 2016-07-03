from flask import render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from DanceCat import app, db, lm, Constants, Helpers, rdb
from DanceCat.Forms import RegisterForm, ConnectionForm, JobForm
from DanceCat.Models import User, AllowedEmail, Connection, \
    Job, Schedule, TrackJobRun
from DanceCat.DBConnect import DBConnect, DBConnectException
import datetime


@lm.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def index():
    return render_template('about.html',
                           title=Constants.PROJECT_NAME)


@app.route('/job')
@login_required
def job():
    jobs = Job.query.all()
    job_lists = []
    for job_object in jobs:
        job_lists.append({
            'id': job_object.id,
            'name': job_object.name,
            'last_updated': job_object.lastUpdated,
            'user_email': job_object.User.email,
            'connection_name': job_object.Connection.name
        })
    return render_template('job/list.html',
                           title=Constants.PROJECT_NAME,
                           jobs=job_lists)


@app.route('/job/create', methods=['GET', 'POST'])
def job_create():
    form = JobForm(request.form)
    form.connectionId.choices = Connection.query.with_entities(Connection.id, Connection.name).all()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_job = Job(name=request.form['name'],
                          annotation=request.form['annotation'],
                          connection_id=request.form['connectionId'],
                          query_string=request.form['query'],
                          user_id=current_user.id)
            db.session.add(new_job)
            db.session.commit()
            return redirect(url_for('job'))
    return render_template('job/form.html',
                           title=Constants.PROJECT_NAME,
                           action='Creating',
                           action_url=url_for('job_create'),
                           form=form)


@app.route('/job/edit/<job_id>', methods=['GET', 'POST'])
@login_required
def job_edit(job_id):
    editing_job = Job.query.get_or_404(job_id)
    form = JobForm(request.form, editing_job)
    form.connectionId.choices = Connection.query.with_entities(Connection.id, Connection.name).all()
    if request.method == 'GET':
        return render_template('job/form.html',
                               title=Constants.PROJECT_NAME,
                               action='Edit',
                               action_url=url_for('job_edit', job_id=job_id),
                               form=form)
    else:
        if form.validate_on_submit():
            form.populate_obj(editing_job)
            db.session.commit()
        return redirect(url_for('job'))


@app.route('/connection')
@login_required
def connection():
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
    conn = Connection.query.with_entities(Connection.id, Connection.type).filter_by(id=connection_id).first()
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

        db_connect = DBConnect(int(request.form['type']), testing_config)
        try:
            db_connect.connection_test(10)
            return jsonify({
                'connected': True
            })
        except DBConnectException:
            return jsonify({
                'connected': False
            })

    return jsonify({
        'connected': False
    })


@app.route('/login', methods=['GET', 'POST'])
def login():
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
    logout_user()
    return redirect(url_for('index'))
