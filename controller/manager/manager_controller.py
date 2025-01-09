from flask import request, render_template, jsonify, flash, redirect, url_for
from sqlalchemy import text
from app import db
import helpers.token as token_helper
import helpers.helper as helper

"""
 This is the function that prepares the data for the 'manager dashboard' view, returns the view with its data
"""


def index(request):
    # from token get id, from the id get the record in the database
    token = request.cookies['token']
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    manager = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not manager:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
    return render_template('manager/index.html', manager=manager)


# id, transaction name, type(credit/debit), amount, trainee Id, timestamp
def get_balance_sheet(request):
    token = request.cookies['token']
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    manager = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not manager:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
    # prepare list of balance sheet records
    # token is the manager id or the manager record
    query = text("SELECT * FROM balance_sheet")
    result_cursor = db.session.execute(query)
    rows = result_cursor.fetchall()
    transactions = []
    for row in rows:
        transactions.append(row._data)
    return render_template("manager/billing.html", transactions=transactions, manager=manager)


def get_email_form(request):
    token = request.cookies['token']
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    manager = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not manager:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
    return render_template("manager/mailing.html", manager=manager)


def send_email(request):
    # sender email credentials 
    token = request.cookies['token']
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    manager = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not manager:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
    recipient = request.form['recipient']
    message = request.form['message']
    subject = request.form['subject']
    sender = manager["email"]
    if not recipient or not message or not subject:
        flash("Missing parameters", "error")
        return redirect(request.referrer)
    response = helper.send_email(recipient=recipient, sender=sender, message=message, subject=subject)
    return redirect(request.referrer)


def get_system_log(request):
    # return render_template("manager/logging.html", manager=manager)
    pass
