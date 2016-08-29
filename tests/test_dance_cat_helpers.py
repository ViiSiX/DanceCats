"""Test script for DanceCat.Helpers module."""

from __future__ import print_function
import datetime
from decimal import Decimal, getcontext as dicimal_get_context
from DanceCat import Helpers


def test_password_encrypt():
    """Test password encrypting and checking function."""
    password = 'some_thing_nice_to !see'

    hashed_password = Helpers.encrypt_password(password)
    assert hashed_password
    assert hashed_password != password

    assert Helpers.check_password(hashed_password, password)
    assert not Helpers.check_password(hashed_password, 'inj3ct   ')
    assert not Helpers.check_password(hashed_password, '')

    hashed_empty_password = Helpers.encrypt_password('')
    assert hashed_empty_password
    assert hashed_empty_password != password


def test_db_password_encrypt():
    """Check DB config encrypting and decrypting function."""
    key = '3ncr9p7 K3Y'
    db_password = 'h3r3 the passw0rD'

    encrypted_config = Helpers.db_credential_encrypt(
        db_password,
        key
    )
    assert encrypted_config

    assert Helpers.db_credential_decrypt(
        encrypted_config,
        key
    ) == db_password


def test_null_handler():
    """Test null_handler function."""
    for value in [0, 0.0, '', None, False]:
        assert not Helpers.null_handler(value)


def test_py2sql_type_convert():
    """Test converter from python objects to SQL type."""
    assert Helpers.py2sql_type_convert(None) == 'NULL'
    dicimal_get_context().prec = 6
    assert Helpers.py2sql_type_convert(
        Decimal(1) / Decimal(7)
    ) == '0.142857'
    assert Helpers.py2sql_type_convert(
        datetime.datetime(2016, 8, 11, 10, 36, 30, 83413)
    ) == '2016-08-11 10:36:30'
    assert Helpers.py2sql_type_convert(8) == 8
    assert Helpers.py2sql_type_convert(8.4) == 8.4


def test_time_checkers():
    """Test time validation functions."""
    assert Helpers.validate_minute_of_hour(24)
    assert not Helpers.validate_minute_of_hour(60)
    assert Helpers.validate_hour_of_day(2)
    assert not Helpers.validate_hour_of_day(24)
    assert Helpers.validate_day_of_week(4)
    assert not Helpers.validate_day_of_week(7)
    assert Helpers.validate_day_of_month(1)
    assert not Helpers.validate_day_of_month(0)


def test_validate_int_between():
    """Test validate_int_between function."""
    assert Helpers.validate_int_between(1, 0, 1)
    assert Helpers.validate_int_between(1, 0, 2)
    assert not Helpers.validate_int_between(4, 1, 3)
    assert not Helpers.validate_int_between(0, 1, 3)
    try:
        Helpers.validate_int_between(3, 5, 2)
        assert False
    except ValueError:
        pass


def test_str2datetime():
    """Test test_str2datetime function."""
    assert Helpers.str2datetime(
        '2016-08-11 10:36:30',
        '%Y-%m-%d %H:%M:%S'
    ) == datetime.datetime(2016, 8, 11, 10, 36, 30)


def test_timer():
    """Test Timer class from Helper."""
    timer = Helpers.Timer()
    assert timer.get_total_time().find("seconds") > 0

    Helpers.sleep(1)
    assert timer.get_total_milliseconds() > 1000
    assert timer.get_total_time().find("seconds") > 0
    assert isinstance(timer.get_total_seconds(), float)
    assert timer.get_total_seconds() > 1

    timer.spend(1)
    assert timer.get_total_time().find("minutes") > 0
    assert timer.get_total_seconds() > 60
