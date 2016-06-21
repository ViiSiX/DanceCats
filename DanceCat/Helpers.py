from Crypto.Cipher import ARC4
import mysql.connector
import pymssql
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
    if not obj:
        return None
    return obj

"""
For references
def sqlserver_connect(config):
    return pymssql.connect(server=config['host'],
                           port=config['port'],
                           user=config['user'],
                           password=config['password'],
                           database=config['database'])
"""