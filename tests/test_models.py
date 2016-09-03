"""Unit tests for DanceCat.Models module."""

from __future__ import print_function
import datetime
from DanceCat import db
from DanceCat import Models
from DanceCat import Constants
import pytest
import sqlalchemy.exc as sqlalchemy_exc


class TestProxiedDictMixin(object):
    """ Unit tests for Models.ProxiedDictMixin class. """
    pass


class TestUserModels(object):
    """ Unit tests for Models.User class. """

    user_1 = {
        'user_email': 'test@test.test',
        'user_password': 'YouShallNotPass'
    }
    user_2 = {
        'user_email': 'cat@ta.lina',
        'user_password': 'Harder,Daddy'
    }

    def test_should_add_new_users(self, app):
        """Test add_allowed_user command."""

        user_1 = Models.User(**self.user_1)
        user_2 = Models.User(**self.user_2)

        db.session.add(user_1)
        db.session.commit()
        datetime_now = datetime.datetime.now()
        datetime_delta_created_on = datetime_now - user_1.created_on
        datetime_delta_last_updated = datetime_now - user_1.last_updated

        assert user_1.get_id() == '1'
        assert user_1.email == self.user_1['user_email']
        assert user_1.password
        assert user_1.is_active
        assert round(datetime_delta_created_on.total_seconds()) == 0
        assert not user_1.last_login
        assert round(datetime_delta_last_updated.total_seconds()) == 0
        assert user_1.version == Constants.MODEL_USER_VERSION
        assert not user_1.connections
        assert not user_1.jobs

        db.session.add(user_2)
        db.session.commit()
        assert user_2.get_id() == '2'
        assert user_2.email == self.user_2['user_email']
        assert user_2.password
        assert user_2.is_active

    @pytest.mark.skip(reason='Should improve exception')
    def test_should_not_add_exited_user(self, app):
        assert app.config.get('SQLALCHEMY_DATABASE_URI')

        user_1 = Models.User(**self.user_1)
        user_2 = Models.User(**self.user_1)

        with pytest.raises(sqlalchemy_exc.IntegrityError_your_exception):
            db.session.add(user_1)
            db.session.add(user_2)
            db.session.commit()

    def test_should_set_last_login_valid_case(self, app):
        user = Models.User(**self.user_1)
        db.session.add(user)
        db.session.commit()

        assert not user.last_login
        user.last_login = datetime.datetime.now()
        datetime_now = datetime.datetime.now()
        datetime_delta_last_login = datetime_now - user.last_login
        db.session.commit()

        assert user.last_login
        assert round(datetime_delta_last_login.total_seconds()) == 0

    def test_should_not_set_last_login_with_invalid_data_type(self, app):
        user = Models.User(**self.user_1)
        db.session.add(user)
        db.session.commit()

        user.last_login = 'InvalidDataType'
        with pytest.raises(sqlalchemy_exc.StatementError):
            db.session.commit()

    @pytest.mark.skip(reason='Should improve data logic')
    def test_should_not_set_last_login_to_null(self, app):
        user = Models.User(**self.user_1)
        db.session.add(user)
        db.session.commit()

        assert not user.last_login
        user.last_login = datetime.datetime.now()
        db.session.commit()

        user.last_login = None
        with pytest.raises(sqlalchemy_exc.StatementError):
            db.session.commit()

    def test_should_set_last_updated_valid_case(self, app):
        user = Models.User(**self.user_1)
        db.session.add(user)
        db.session.commit()

        assert user.last_updated
        previous_last_updated = user.last_updated
        user.last_updated = datetime.datetime.now()
        datetime_now = datetime.datetime.now()
        datetime_delta_last_updated = datetime_now - user.last_updated
        db.session.commit()

        assert user.last_updated
        assert round(datetime_delta_last_updated.total_seconds()) == 0
        assert user.last_updated != previous_last_updated
