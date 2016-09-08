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


class TestUserModel(object):
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
        user_1 = Models.User(**self.user_1)
        user_2 = Models.User(**self.user_2)

        # db is implicitly created in `app` pytest.fixture
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

    def test_user_is_active(self, app):
        user = Models.User(**self.user_1)
        db.session.add(user)
        db.session.commit()

        assert user.is_active is True
        user.is_active = False
        db.session.commit()
        assert user.is_active is False

    @pytest.mark.skip(reason='https://github.com/scattm/DanceCat/issues/83')
    def test_should_get_user_version(self, app):
        user = Models.User(**self.user_1)
        db.session.add(user)
        db.session.commit()

        assert user.version == Constants.MODEL_USER_VERSION
        user.version = 15
        db.session.add(user)
        db.session.commit()
        assert user.version == 15
        user.version = 'InvalidDataType'
        db.session.add(user)
        with pytest.raises(ValueError):
            db.session.commit()

    def test_should_print_user_instance(self, app, capfd):
        user = Models.User(**self.user_1)
        db.session.add(user)
        db.session.commit()
        print (user)
        out, err = capfd.readouterr()
        assert out == '<User test@test.test - Id 1>\n'
        assert not err


class TestAllowedEmailModel(object):
    """ Unit tests for Models.AllowedEmail class. """

    user_email = 'test@test.test'

    def test_should_able_to_add(self, app, capfd):
        allowed_email = Models.AllowedEmail(allowed_email=self.user_email)
        db.session.add(allowed_email)
        db.session.commit()
        assert allowed_email.version == Constants.MODEL_ALLOWED_EMAIL_VERSION
        assert allowed_email.email == self.user_email
        assert allowed_email.allowed_email_id == 1

    def test_should_not_add_dulicated_email(self, app):
        allowed_email = Models.AllowedEmail(allowed_email=self.user_email)
        db.session.add(allowed_email)
        db.session.commit()
        allowed_email_2 = Models.AllowedEmail(allowed_email=self.user_email)
        db.session.add(allowed_email_2)
        with pytest.raises(sqlalchemy_exc.IntegrityError):
            db.session.commit()

    def test_should_not_add_invalid_email_address(self, app):
        with pytest.raises(ValueError):
            Models.AllowedEmail(allowed_email='Invalid')
