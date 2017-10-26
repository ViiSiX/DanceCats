"""Test script for DanceCats.Helpers module."""
# -*- coding: utf-8 -*-

from __future__ import print_function
import datetime
from decimal import Decimal, getcontext as dicimal_get_context
from Crypto.Cipher.AES import block_size as AES_block_size
from Crypto import Random
from DanceCats import Helpers
import pytest
import time


def test_encrypt_password():
    """Test password encrypting and checking function."""
    password = 'some_thing_nice_to !see'

    hashed_password = Helpers.encrypt_password(password)
    assert hashed_password
    assert hashed_password != password

    with pytest.raises(AttributeError) as exec_info:
        Helpers.encrypt_password(True)
    assert "'bool' object has no attribute 'encode'" in exec_info.value

    assert Helpers.check_password(hashed_password, password)
    assert not Helpers.check_password(hashed_password, 'inj3ct   ')
    assert not Helpers.check_password(hashed_password, '')

    hashed_empty_password = Helpers.encrypt_password('')
    assert hashed_empty_password
    assert hashed_empty_password != password


def test_rc4_encrypt_decrypt():
    """Check RC4 crypto functions."""
    key = '3ncr9p7 K3Y'
    db_password = 'h3r3 the passw0rD'

    encrypted_config = Helpers.rc4_encrypt(
        db_password,
        key
    )
    assert encrypted_config

    assert Helpers.rc4_decrypt(
        encrypted_config,
        key
    ) == db_password

    with pytest.raises(TypeError) as except_info:
        assert Helpers.rc4_encrypt(None, key)
    assert 'argument must be string or read-only buffer, not None' \
        in except_info.value


def test_aes_helpers():
    """Check AES helper functions."""
    keys_list = [
        'A9ll j',
        '0123-0123-0123-0123-0123-0123-01',
        '0123-0123-0123-0123-0123-0123-0123',
        list('moo')
    ]
    raw_lists = [
        '', '012 aj/', '01234567890123',
        '0123456789abcdef', '0123456789abcdef=Z0/?'
    ]

    # Valid
    for key in keys_list:
        assert len(Helpers.aes_key_pad(key)) == 32

    # Should not be empty string
    with pytest.raises(ValueError) as except_info:
        Helpers.aes_key_pad('')
    assert 'Key should not be empty!' in except_info.value

    # Valid
    for raw in raw_lists:
        padded_raw = Helpers.aes_raw_pad(raw)
        assert len(padded_raw) % AES_block_size == 0
        assert raw in padded_raw

    with pytest.raises(TypeError) as except_info:
        Helpers.aes_raw_pad({'a': 'ops'})
    assert 'Context should be a string!' in except_info.value

    with pytest.raises(ValueError) as except_info:
        raw = Random.new().read(1000)
        Helpers.aes_raw_pad(raw)
    assert 'Encrypt context was too long (>999).' in except_info.value

    assert Helpers.aes_raw_unpad(
        Helpers.aes_raw_pad("12K la0'V")
    ) == "12K la0'V"


def test_aes_password_encrypt_decrypt():
    """Check AES crypto functions."""
    key = '3ncr9p7 K3Y'
    valid_passwords = [
        'h3r3 the passw0rD',
        '01234567890123'
    ]
    db_password_utf8 = u'trời ơi!'

    for password in valid_passwords:
        encrypted_config = Helpers.aes_encrypt(
            password,
            key
        )
        assert encrypted_config

        assert Helpers.aes_decrypt(
            encrypted_config,
            key
        ) == password

    assert Helpers.aes_decrypt(
        Helpers.aes_encrypt(
            db_password_utf8,
            key
        ),
        key
    ) == db_password_utf8.encode('utf-8')

    with pytest.raises(TypeError) as except_info:
        assert Helpers.aes_encrypt(None, key)
    assert 'Context should be a string!' \
        in except_info.value


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


def test_is_in_range():
    """Test is_in_range function."""
    assert Helpers.is_in_range(1, 0, 1)
    assert Helpers.is_in_range(1, 0, 2)
    assert not Helpers.is_in_range(4, 1, 3)
    assert not Helpers.is_in_range(0, 1, 3)
    try:
        Helpers.is_in_range(3, 5, 2)
        assert False
    except ValueError:
        pass


def test_str2datetime():
    """Test str2datetime function."""
    assert Helpers.str2datetime(
        '2016-08-11 10:36:30',
        '%Y-%m-%d %H:%M:%S'
    ) == datetime.datetime(2016, 8, 11, 10, 36, 30)


def test_generate_runtime():
    """ Test generate_runtime function. """
    runtime = Helpers.generate_runtime()
    now = int(time.time()*1000)
    assert round(now - runtime) == 0


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


def test_is_valid_format_email():
    """Test is_valid_format_email function."""
    valid_emails = [
        'test@test.test',
        'so.long.i.dont.care.test@te.te.te',
        'iAmS0lesS_wAnNa@B3aUt1.Fu1.lol'
    ]
    invalid_emails = [
        'invalid email bleh bleh',
        'user@mail',
        'usermail@',
        '@usermail',
        'user@mail.',
        'user@.mail',
        'user.mail@domain',
        'user.@mail',
        '.user@mail'
    ]
    for email in valid_emails:
        assert Helpers.is_valid_format_email(email)
    for email in invalid_emails:
        assert not Helpers.is_valid_format_email(email)
    with pytest.raises(TypeError):
        Helpers.is_valid_format_email(list)
