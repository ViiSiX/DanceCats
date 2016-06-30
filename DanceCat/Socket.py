import functools
import time
from flask_login import current_user
from flask_socketio import disconnect, emit
from DanceCat import socket_io, db, config
from DanceCat.DBConnect import DBConnect, DBConnectException
from DanceCat.Models import Connection


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


@socket_io.on('s_query')
@authenticated_only
def test_query(received_data):
    """
    :param received_data: Dictionary with connection id and query
    :type received_data: dict
    """
    runtime = int(time.time() * 1000)
    if type(received_data) == dict:
        connection_id = received_data.get('connectionId', 0)
        query = received_data.get('query', '')

        if query == '':
            return emit('r_query', {
                'status': -1,
                'seq': runtime,
                'error': 'Query is required!'
            })

        testing_connection = Connection.query.get(connection_id)
        if testing_connection is not None:
            try:
                connector = DBConnect(testing_connection.type,
                                      testing_connection.db_config_generator(),
                                      convert_sql=True,
                                      dict_format=True,
                                      timeout=5)
                connector.connect()
                connector.execute(query)
                return emit('r_query', {
                    'status': 0,
                    'data': connector.fetch_many(size=config.get('QUERY_TEST_LIMIT', 10)),
                    'header': connector.columns_name,
                    'seq': runtime
                })
            except DBConnectException as e:
                print e
                return emit('r_query', {
                    'status': -1,
                    'data': 'None',
                    'seq': runtime,
                    'error': str(e),
                    'error_ext': [str(e.trace_back)]
                })

        else:
            return emit('r_query', {
                'status': -1,
                'seq': runtime,
                'error': 'Connection not found!'
            })
    else:
        return emit('r_query', {
            'status': -1,
            'seq': runtime,
            'error': 'Wrong data received!'
        })
