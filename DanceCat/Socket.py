import functools
from flask_login import current_user
from flask_socketio import disconnect, emit
from DanceCat import socket_io, config, Constants, Helpers
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
                connector = DBConnect(running_connection.type,
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
            except DBConnectException as e:
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
