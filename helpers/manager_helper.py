 from flask import jsonify, redirect, url_for, flash
from sqlalchemy import text
import helpers.token as tokenHelper
from app import app
from app import db


def verify_manager(token):
    verified = False
    if not token and token != "":
        return verified
    payload = tokenHelper.verify_token(token)
    if not payload:
        return verified
    verified = True
    data = [verified, payload]
    return jsonify(data)
