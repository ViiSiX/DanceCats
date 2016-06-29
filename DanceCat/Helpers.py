from Crypto.Cipher import ARC4
import datetime
import base64
import hashlib
import uuid


def encrypt_password(password):
    salt = uuid.uuid4().hex
    return hashlib.sha512(salt.encode() + password.encode()).hexdigest() + ':' + salt


def check_password(hashed_password, input_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha512(salt.encode() + input_password.encode()).hexdigest()


def db_credential_encrypt(credential_string, secret_string):
    sec_obj = ARC4.new(secret_string)
    enc_bin = sec_obj.encrypt(credential_string)
    enc_str = base64.b64encode(enc_bin)
    return enc_str


def db_credential_decrypt(b64_string, secret_string):
    sec_obj = ARC4.new(secret_string)
    enc_bin = base64.b64decode(b64_string)
    credential_string = sec_obj.decrypt(enc_bin)
    return credential_string


def null_handler(obj):
    return None if not obj else obj


def py2sql_type_convert(obj):
    if obj is None:
        return 'NULL'
    if type(obj) is datetime.datetime:
        return u'{value}'.format(value=obj.strftime('%Y-%m-%d %H:%M:%S'))
    return obj


def validate_int_between(value, floor, cell):
    return True if value <= floor <= cell else False


def validate_minute_of_hour(value):
    return validate_int_between(value, 0, 59)


def validate_hour_of_day(value):
    return validate_int_between(value, 0, 23)


def validate_day_of_week(value):
    return validate_int_between(value, 0, 6)


def validate_day_of_month(value):
    return validate_int_between(value, 1, 31)
