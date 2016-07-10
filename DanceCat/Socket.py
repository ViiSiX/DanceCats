import functools
import Helpers
import Constants
from flask import url_for
from flask_login import current_user
from flask_socketio import disconnect, emit
from DanceCat import socket_io, config, db
from DanceCat.DatabaseConnector import DatabaseConnector, DatabaseConnectorException
from DanceCat.Models import Connection, Job, TrackJobRun


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


@socket_io.on(Constants.WS_QUERY_RECEIVE)
@authenticated_only
def run_query(received_data):
    """
    :param received_data: Dictionary with connection id and query
    :type received_data: dict
    """
    runtime = Helpers.generate_runtime()
    if isinstance(received_data, dict):
        connection_id = received_data.get('connectionId', 0)
        query = received_data.get('query', '')

        if query == '':
            return emit(Constants.WS_QUERY_SEND, {
                'status': -1,
                'seq': runtime,
                'error': 'Query is required!'
            })

        running_connection = Connection.query.get(connection_id)
        if running_connection is not None:
            try:
                connector = DatabaseConnector(running_connection.type,
                                              running_connection.db_config_generator(),
                                              sql_data_type=True,
                                              dict_format=True,
                                              timeout=config.get('DB_TIMEOUT', 60))
                connector.connection_test(10)
                connector.connect()
                connector.execute(query)
                ret_data = connector.fetch_many(size=config.get('QUERY_TEST_LIMIT', 10))
                connector.close()
                return emit(Constants.WS_QUERY_SEND, {
                    'status': 0,
                    'data': ret_data,
                    'header': connector.columns_name,
                    'seq': runtime
                })
            except DatabaseConnectorException as e:
                print e
                return emit(Constants.WS_QUERY_SEND, {
                    'status': -1,
                    'data': 'None',
                    'seq': runtime,
                    'error': str(e),
                    'error_ext': [str(e.trace_back)]
                })

        else:
            return emit(Constants.WS_QUERY_SEND, {
                'status': -1,
                'seq': runtime,
                'error': 'Connection not found!'
            })

    else:
        return emit(Constants.WS_QUERY_SEND, {
            'status': -1,
            'seq': runtime,
            'error': 'Wrong data received!'
        })


@socket_io.on(Constants.WS_TRACKERS_RECEIVE)
@authenticated_only
def get_trackers():
    runtime = Helpers.generate_runtime()

    query = db.session.query(TrackJobRun, Job).join(Job)
    trackers = query.order_by(TrackJobRun.id.desc()).limit(20).all()
    trackers_list = []

    for tracker in trackers:
        if tracker.TrackJobRun.check_expiration():
            db.session.commit()
        trackers_list.append({
            'id': tracker.TrackJobRun.id,
            'jobName': tracker.Job.name,
            'database': tracker.Job.Connection.database,
            'status': Constants.JOB_TRACKING_STATUS_DICT[tracker.TrackJobRun.status]['name'],
            'ranOn': Helpers.py2sql_type_convert(tracker.TrackJobRun.ranOn),
            'duration': tracker.TrackJobRun.duration,
            'csv': url_for('job_result', tracker_id=tracker.TrackJobRun.id, result_type='csv') if
            tracker.TrackJobRun.status == Constants.JOB_RAN_SUCCESS else None,
            'xlsx': url_for('job_result', tracker_id=tracker.TrackJobRun.id, result_type='xlsx') if
            tracker.TrackJobRun.status == Constants.JOB_RAN_SUCCESS else None,
        })

    return emit(Constants.WS_TRACKERS_SEND, {
        'seq': runtime,
        'trackers': trackers_list
    })
