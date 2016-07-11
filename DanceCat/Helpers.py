"""Helper functions that will be used through all the application."""

from decimal import Decimal
import datetime
import time
import base64
import hashlib
import uuid
from Crypto.Cipher import ARC4


def encrypt_password(password):
    """
    Encrypt the clear-text password to SHA hash.

    :param password: Password in clear text.
    :type password: str
    :return: Hashed string.
    """
    salt = uuid.uuid4().hex
    return hashlib.sha512(salt.encode() + password.encode()).hexdigest() + ':' + salt


def check_password(hashed_password, input_password):
    """
    Check if the input password is correct or not.

    :param hashed_password:
        Hashed string of previous input password.
    :type hashed_password: str
    :param input_password:
        Checking password in clear text.
    :type input_password: str
    :return: True if the clear text password is correct else False.
    """
    password, salt = hashed_password.split(':')
    return password == hashlib.sha512(salt.encode() + input_password.encode()).hexdigest()


def db_credential_encrypt(credential_string, secret_string):
    """
    Encrypt the clear text credential string into a Rivest Cipher 4 stream
        then encode it into a Base64 string.

    :param credential_string:
        Credential string that need to be encrypt.
    :type credential_string: str
    :param secret_string:
        The secret string that will be used to encrypt the
        credential string.
    :type secret_string: str
    :return: Encrypted RC4 stream in Base64 string.
    """
    sec_obj = ARC4.new(secret_string)
    enc_bin = sec_obj.encrypt(credential_string)
    enc_str = base64.b64encode(enc_bin)
    return enc_str


def db_credential_decrypt(b64_string, secret_string):
    """
    Given a RC4 stream in Base64 and a secret string,
        return the clear text credential.

    :param b64_string: RC4 stream in Base64 string.
    :type b64_string: str
    :param secret_string:
        The secret string that will be used to encrypt the
        credential string.
    :type secret_string: str
    :return: Clear text credential.
    """
    sec_obj = ARC4.new(secret_string)
    enc_bin = base64.b64decode(b64_string)
    credential_string = sec_obj.decrypt(enc_bin)
    return credential_string


def null_handler(obj):
    """Given any object, return None if the value is similar to NULL."""
    return None if not obj else obj


def py2sql_type_convert(obj):
    """Given any object, return the same object in SQL style."""
    if obj is None:
        return 'NULL'
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, datetime.datetime):
        return u'{value}'.format(value=obj.strftime('%Y-%m-%d %H:%M:%S'))
    return obj


def validate_int_between(value, floor, cell):
    """
    Given three integer number x, n, m with n <= m.

    :return: True if n <= x <= m else False.
    """
    if floor > cell:
        raise ValueError("Floor is larger than Cell in this comparison.")
    return True if value <= floor <= cell else False


def validate_minute_of_hour(value):
    """Validate if a number is minute of an hour."""
    return validate_int_between(value, 0, 59)


def validate_hour_of_day(value):
    """Validate if a number is hour of a day."""
    return validate_int_between(value, 0, 23)


def validate_day_of_week(value):
    """Validate if a number is day of a week."""
    return validate_int_between(value, 0, 6)


def validate_day_of_month(value):
    """Validate if a number is minute of hour."""
    return validate_int_between(value, 1, 31)


def generate_runtime():
    """
    Generate an epoch timestamp in milliseconds
        at the this function run.

    :return: Epoch timestamp in milliseconds.
    """
    return int(time.time() * 1000)


def sleep(seconds):
    """Sleep for the input seconds."""
    time.sleep(seconds)


class Timer(object):

    """
    Timer class is used to track the total runtime
        since the class construction.
    """

    def __init__(self):
        """Timer constructor, set a time object."""
        self.start_time = time.time() * 1000

    def get_total_time(self):
        """

        :return: Total runtime since the class construction
            in human readable string.
        """
        total_time = time.time() * 1000 - self.start_time

        if total_time >= 60000:
            return "%d minutes %d seconds" % (
                total_time / 60000, (total_time % 60000) / 1000
            )

        elif total_time >= 1000:
            return "%d seconds" % (total_time / 1000)

        else:
            return "%d milliseconds" % total_time

    def get_total_milliseconds(self):
        """

        :return: Total runtime since the class construction
            in milliseconds.
        """
        return time.time() * 1000 - self.start_time
