 import jwt
from datetime import datetime, timedelta
from flask import flash
import os

""" 
    Generates a token for authentication. 
    It should use a module that i currently can't remember its name 
    It take a parameter, that is the user row in the database, encrypts it, and returns its hash.
"""


def generate_token(user_record):
    # TODO: token expiration
    # generate token
    token = jwt.encode(
        user_record, os.getenv('SECRET_KEY'), algorithm='HS256')
    return token


"""
    takes in a token, returns the encrypted data within it. 
    So if we assume we've encrypted the user's row in the database, this shall retrieve it. 
"""


def verify_token(token):
    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
        # if it reaches this line, this means that it's decoded correctly
        # check expiration time
        # if 'expire' in payload:
        #     exp_time = datetime.strptime(payload['expire'], '%Y-%m-%d %H:%M:%S')
        #     if datetime.utcnow() > exp_time:
        #         return False
        #     # token not expired and return data
        #     payload = {
        #         "userID": payload["userID"],
        #         "password": payload["password"],
        #         "classification": payload["classification"],
        #         "email": payload["email"],
        #     }
        #     return payload
        # else:
        #     return False
        return payload
    except jwt.exceptions.DecodeError:
        # if it reaches this line, this means that it's decoded incorrectly
        return False


"""
    Helper function that checks the token to authorize the user
"""


def authorize_user(token):
    # if there's no token -> halt process
    if not token:
        return flash('Unauthorized user, no token', 'error')
    # verify and decode the token
    payload = verify_token(token, secret_key=os.getenv('SECRET_KEY'))
    if isinstance(payload, dict):
        return payload
    else:
        return flash('User is not authorized.', 'error')
