"""Unit tests for DanceCat.Models.Connection model."""

from __future__ import print_function
from DanceCat import db
from DanceCat import Models
from DanceCat import Constants
from DanceCat import Helpers
import datetime
import pytest


class TestConnectionModel(object):
    """Unit test for Connection model class."""

    creator_user_id = 1
    db_host = 'db.my-domain.com'
    db_name = 'barking_dog'
    db_user = 'nemo'
    db_password = 'sniffing-pixel'
    connection_skeleton = {
        'host': db_host,
        'database': db_name,
        'user_name': db_user,
        'creator_user_id': creator_user_id
    }

    def test_would_add_new_connection(self, app_setup_to_add_user):
        """Test if connection will be added."""
        app = app_setup_to_add_user['app']

        assert app_setup_to_add_user['user_id'] == self.creator_user_id

        db_name = 'normal connection'
        connection = Models.Connection(
            name=db_name,
            db_type=Constants.DB_MYSQL,
            port=3306,
            password=self.db_password,
            **self.connection_skeleton
        )
        assert connection.connection_id is None
        db.session.add(connection)
        db.session.commit()
        cur_time = datetime.datetime.now()
        assert connection.connection_id == 1

        from_db_connection = \
            Models.Connection.query.get(connection.connection_id)
        assert from_db_connection.name == db_name
        assert from_db_connection.type == Constants.DB_MYSQL
        assert from_db_connection.port == 3306
        assert Helpers.aes_decrypt(
            from_db_connection.password,
            app.config.get('DB_ENCRYPT_KEY')
        ) == self.db_password
        assert from_db_connection.host == self.db_host
        assert from_db_connection.database == self.db_name
        assert from_db_connection.user_name == self.db_user
        assert from_db_connection.user_id == self.creator_user_id
        datetime_delta_last_updated_on = \
            cur_time - from_db_connection.last_updated
        assert round(datetime_delta_last_updated_on.total_seconds()) == 0
        assert from_db_connection.version == Constants.MODEL_CONNECTION_VERSION
        assert str(from_db_connection) == \
            '<Connection "normal connection" - Id 1>'

    def test_would_raise_error_missing_key_params(self,
                                                  app_setup_to_add_user
                                                  ):
        """Test if errors will be raise on missing key params."""
        with pytest.raises(TypeError) as exec_info:
            Models.Connection()
        assert '__init__() takes exactly' in str(exec_info)

        # Missing DB Type
        with pytest.raises(TypeError) as exec_info:
            Models.Connection(**self.connection_skeleton)
        assert '__init__() takes exactly' in str(exec_info)

        with pytest.raises(TypeError) as exec_info:
            Models.Connection(
                db_type=None,
                **self.connection_skeleton
            )
        assert "Connection's type cannot be empty or None." in str(exec_info)

        for arg in ['host', 'database', 'user_name', 'creator_user_id']:
            kwargs = self.connection_skeleton.copy()
            kwargs.pop(arg)
            kwargs['db_type'] = Constants.DB_MYSQL
            with pytest.raises(TypeError) as exec_info:
                Models.Connection(**kwargs)
            assert '__init__() takes exactly' in str(exec_info) \
                or 'cannot be empty or None' in str(exec_info)

            kwargs = self.connection_skeleton.copy()
            kwargs[arg] = None
            kwargs['db_type'] = Constants.DB_MYSQL
            with pytest.raises(TypeError) as exec_info:
                Models.Connection(**kwargs)
            assert 'cannot be empty or None' in str(exec_info)

    def test_would_raise_invalid_connection_type(self,
                                                 app_setup_to_add_user
                                                 ):
        """Test if ValueError would be raised if connection type is invalid."""
        with pytest.raises(ValueError):
            Models.Connection(1000, **self.connection_skeleton)

    def test_would_not_raise_missing_unrequired_params(self,
                                                       app_setup_to_add_user
                                                       ):
        """Test if errors would not be raised on missing un-required params."""
        min_connection = Models.Connection(
            db_type=Constants.DB_MYSQL,
            **self.connection_skeleton
        )
        db.session.add(min_connection)
        db.session.commit()
        assert min_connection.connection_id == 1

    def test_would_not_encrypt_none_password(self,
                                             app_setup_to_add_user
                                             ):
        """Do not encrypt the none password, check it."""
        none_pass_connection = Models.Connection(
            db_type=Constants.DB_MYSQL,
            **self.connection_skeleton
        )
        db.session.add(none_pass_connection)
        db.session.commit()
        assert none_pass_connection.connection_id == 1

        from_db_connection = \
            Models.Connection.query.get(none_pass_connection.connection_id)
        assert from_db_connection.password is None

    def test_would_generate_normal_db_config(self,
                                             app_setup_to_add_user
                                             ):
        """Test if Connection could generate the right config."""
        app = app_setup_to_add_user['app']
        expected_values = {
            'user': self.db_user,
            'host': self.db_host,
            'database': self.db_name,
            'port':
                Constants.CONNECTION_TYPES_DICT
                [Constants.DB_MYSQL]['default_port']
        }

        none_pass_connection = Models.Connection(
            db_type=Constants.DB_MYSQL,
            **self.connection_skeleton
        )
        db.session.add(none_pass_connection)
        db.session.commit()
        none_pass_config = \
            Models.Connection.query.get(
                none_pass_connection.connection_id
            ).db_config_generator()

        for key, value in expected_values.items():
            assert none_pass_config[key] == value
        assert 'password' not in none_pass_config

        expected_port = 4567
        expected_values['port'] = expected_port
        expected_values['password'] = self.db_password
        normal_connection = Models.Connection(
            db_type=Constants.DB_MYSQL,
            port=expected_port,
            password=self.db_password,
            **self.connection_skeleton
        )
        db.session.add(normal_connection)
        db.session.commit()

        normal_config = \
            Models.Connection.query.get(
                normal_connection.connection_id
            ).db_config_generator()
        for key, value in expected_values.items():
            assert normal_config[key] == value

        normal_connection.version = 1
        normal_connection.password = Helpers.rc4_encrypt(
            self.db_password,
            app.config.get('DB_ENCRYPT_KEY')
        )
        db.session.commit()
        out_version_config = \
            Models.Connection.query.get(
                normal_connection.connection_id
            ).db_config_generator()
        for key, value in expected_values.items():
            assert out_version_config[key] == value
