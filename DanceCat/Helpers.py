"""Helper functions that will be used through all the application."""

from decimal import Decimal
import datetime
import time
import base64
import hashlib
import uuid
from Crypto import Random
from Crypto.Cipher import ARC4, AES


def encrypt_password(password):
    """
    Encrypt the clear-text password to SHA hash.

    :param password: Password in clear text.
    :type password: str
    :return: Hashed string.
    """
    salt = uuid.uuid4().hex
    return \
        hashlib.sha512(salt.encode() + password.encode()).\
        hexdigest() + ':' + salt


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
    return \
        password == hashlib.sha512(salt.encode() + input_password.encode()).\
        hexdigest()


def rc4_encrypt(credential_string, secret_string):
    """
    Encrypt the credential.

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


def rc4_decrypt(b64_string, secret_string):
    """
    Decrypt the credential.

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


def aes_key_pad(key):
    """
    Return padded key string used in AES encrypt function.

    :param key: A key string.
    :return: Padded key string.
    """
    aes_key_length = 32
    while len(key) < aes_key_length:
        key += key
    return key[:aes_key_length]


def aes_raw_pad(raw):
    """
    Return padded raw string that will be encrypted by AES encrypt function.

    :param raw: Raw string that will be padded.
    :return: Padded raw string.
    """
    if len(raw) > 999:
        raise ValueError('Encrypt context was too long (>999).')

    len_leaded_raw = '{raw_len:03d}{raw_string}'.format(
        raw_len=len(raw),
        raw_string=raw
    )

    while len(len_leaded_raw) % AES.block_size > 0:
        len_leaded_raw += len_leaded_raw

    return len_leaded_raw


def aes_raw_unpad(padded_raw):
    """Return original raw string from padded raw string."""
    return padded_raw[:int(padded_raw[:3]) + 3][3:]


def aes_encrypt(credential_string, key):
    """
    Encrypt a raw content by AES crypto.

    Given a raw credential string and a secret key, this function will
    use AES crypto to encrypt the credential.
    AES required raw content's length a multiple of block size (16)
    and key's length in 16, 24 and 32. In this function we use 32.

    :param credential_string:
        Credential string that need to be encrypt with length less than 1000.
    :param key:
        The key string that will be used to encrypt the credential string.
    :return:
        Base64 string of encrypted credential.
    """
    key = b'{key_string}'.format(key_string=aes_key_pad(key))
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_ECB, iv)
    return base64.b64encode(
        iv + cipher.encrypt(b'{credential_string}'.format(
            credential_string=aes_raw_pad(credential_string)
        ))
    )


def aes_decrypt(b64_string, key):
    """
    Decrypt AES encrypted credential.

    :param b64_string:
        Base64 string of encrypted credential.
    :param key:
        The key string that will be used to decrypt the credential string.
    :return:
        Original raw string.
    """
    key = b'{key_string}'.format(key_string=aes_key_pad(key))
    encrypted_string = base64.b64decode(b64_string)
    iv = encrypted_string[:AES.block_size]
    cipher = AES.new(key, AES.MODE_ECB, iv)
    return aes_raw_unpad(cipher.decrypt(encrypted_string[AES.block_size:]))


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


def is_in_range(value, floor, cell):
    """
    Given three integer number x, n, m with n <= m.

    :return: True if n <= x <= m else False.
    """
    if floor > cell:
        raise ValueError("Floor is larger than Cell in this comparison.")
    return True if floor <= value <= cell else False


def validate_minute_of_hour(value):
    """Validate if a number is minute of an hour."""
    return is_in_range(value, 0, 59)


def validate_hour_of_day(value):
    """Validate if a number is hour of a day."""
    return is_in_range(value, 0, 23)


def validate_day_of_week(value):
    """Validate if a number is day of a week."""
    return is_in_range(value, 0, 6)


def validate_day_of_month(value):
    """Validate if a number is minute of hour."""
    return is_in_range(value, 1, 31)


def generate_runtime():
    """
    Generate an epoch timestamp in milliseconds at the this function run.

    :return: Epoch timestamp in milliseconds.
    """
    return int(time.time() * 1000)


def sleep(seconds):
    """Sleep for the input seconds."""
    time.sleep(seconds)


def str2datetime(dt_string, format_string):
    """Convert string to datetime object follow format string."""
    return datetime.datetime.strptime(dt_string, format_string)


class Timer(object):
    """
    Timer Class.

    Timer class is used to track the total runtime
    since the class construction.
    """

    def __init__(self):
        """Timer constructor, set a time object."""
        self.start_time = generate_runtime()

    def get_total_time(self):
        """Return human readable total runtime since class construction."""
        total_time = time.time() * 1000 - self.start_time

        if total_time >= 60000:
            return "{minutes} minutes {seconds} seconds".format(
                minutes=total_time / 60000,
                seconds=(total_time % 60000) / 1000
            )

        elif total_time >= 1000:
            return "{seconds} seconds".format(seconds=total_time / 1000)

        else:
            return "{milliseconds} milliseconds".\
                format(milliseconds=total_time)

    def spend(self, minutes):
        """
        Simulate of spending a number of minutes.

        :param minutes: number of minutes that has already spent.
        :return: Set the initial time of this class.
        """
        self.start_time -= 60000 * minutes

    def get_total_milliseconds(self):
        """Return total runtime since class construction in milliseconds."""
        return time.time() * 1000 - self.start_time

    def get_total_seconds(self):
        """Return total runtime since class construction in seconds."""
        return float(self.get_total_milliseconds()) / 1000
