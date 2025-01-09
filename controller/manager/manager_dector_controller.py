from flask import request, render_template, jsonify, flash, url_for, redirect
from sqlalchemy import text
from app import db
import secrets
import helpers.manager_helper as mghelper
import helpers.token as token_helper
import helpers.helper as helper

"""
    This is the function that prepares data for the 'pending advisors' view, and returns the view with its data 
"""


def get_pending_advisors(request):
    # token is the manager id or the manager record
    token = request.cookies['token']
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    manager = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not manager:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
    query = text("SELECT * from advisors where status = 'pending'")
    result_cursor = db.session.execute(query)
    rows = result_cursor.fetchall()
    advisors = []
    for row in rows:
        advisors.append(row._data)
    return render_template('manager/advisor/pending_advisors.html', manager=manager, advisors=advisors)


"""
    This is the controller function that handles the approve button in the pending advisors view
"""


def approve_advisors_registration(request):
    token = request.cookies['token']
    # make sure manager is authorized
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    manager = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not manager:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
    # get hidden form data
    advisorID = request.form['advisorID']
    advisorEmail = request.form['advisorEmail']
    pass_length = 7
    # secret is python module that generates passwords according to ur prefered length
    password = secrets.token_urlsafe(pass_length)
    # insert advisor to user table first to link it to advisor table using userID(PK->FK relationship)
    user_query = text("INSERT INTO users (password, email, classification) VALUES (:password, :email, 'advisor')")
    user_cursor = db.session.execute(user_query, {'password': password, 'email': advisorEmail})
    db.session.commit()
    if not user_cursor:
        flash('Failed to approve advisor', 'error')
        return redirect(url_for('manager.get_pending_advisors_view'))
    # get userID from previous query
    userID = user_cursor.lastrowid
    # update advisor table with userID
    advisor_query = text("UPDATE advisors SET status = 'active', userID = :userID  WHERE advisorID = :advisorID")
    advisor_cursor = db.session.execute(advisor_query, {'userID': userID, 'advisorID': advisorID})
    advisor_rows = advisor_cursor.rowcount
    db.session.commit()
    if not advisor_rows:
        flash('Failed to approve advisor', 'error')
        return redirect(url_for('manager.get_pending_advisors_view'))
    flash('Advisor approved successfully', 'success')
    # get the user so we can send him his data
    user = db.session.execute(text("SELECT password, email from users where userID = :userID"),
                              {"userID": userID}).fetchone()
    # send credentials to the trainee
    recipient = user[1]
    sender = manager["email"]
    message = """
    Dear advisor,

    Welcome to our team of esteemed advisors! We are delighted to inform you that your application to join our network of advisors has been approved.

    Your expertise and experience will undoubtedly contribute significantly to our mission of providing exceptional guidance and support to our clients. We believe your valuable insights will make a meaningful difference in the lives of those seeking your assistance.

    We are excited to have you on board, and we look forward to a fruitful collaboration. Together, we can empower individuals and help them navigate their path towards success.


    Here are your login credentials, Don't share them with anyone
    Email: {0}
    Password: {1}
    Note: you can change your information anytime. 
    
    Once again, welcome to our community of advisors!

    Best regards,
    {2} from TMS.
        """.format(user[1], user[0], manager["fullname"])
    subject = "Welcome to TMS!"
    response = helper.send_email(recipient=recipient, sender=sender, message=message, subject=subject)

    return redirect(url_for('manager.get_pending_advisors_view'))


"""
    This is the controller function that handles the reject button in the pending advisors view
"""


def reject_advisors_registration(request):
    token = request.cookies['token']
    # make sure manager is authorized
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    manager = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not manager:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
    # get hidden form data
    advisorID = request.form['advisorID']
    # update advisor table with userID
    advisor_query = text("UPDATE advisors SET status = 'rejected' WHERE advisorID = :advisorID")
    advisor_cursor = db.session.execute(advisor_query, {'advisorID': advisorID})
    advisor_rows = advisor_cursor.rowcount
    # commit changes to db
    db.session.commit()
    if not advisor_rows:
        flash('Failed to approve advisor', 'error')
        return redirect(url_for('manager.get_pending_advisors_view'))
    flash('Advisor rejected successfully', 'success')
    # get the user so we can send him his data
    user = db.session.execute(text("SELECT  email, fullName from advisors where advisorID = :advisorID"),
                              {"advisorID": advisorID}).fetchone()
    # send credentials to the trainee
    recipient = user[0]
    sender = manager["email"]
    message = """
    Dear {0},

    Thank you for your interest in our system. Unfortunately, we are unable to accept your signup at this time. We appreciate your understanding.

    Best regards,
    {1} from TMS
            """.format(user[1], manager["fullname"])
    subject = "Regarding Your Signup"
    response = helper.send_email(recipient=recipient, sender=sender, message=message, subject=subject)

    return redirect(url_for('manager.get_pending_advisors_view'))


def get_advisor_account(request):
    token = request.cookies['token']
    # make sure manager is authorized
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    manager = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not manager:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
    # get hidden form data
    query = text("SELECT * from advisors where status = 'inreview'")
    result_cursor = db.session.execute(query)
    rows = result_cursor.fetchall()
    advisors = []
    for row in rows:
        advisors.append(row._data)
    return render_template("manager/advisor/advisor_account_modification.html", manager=manager, advisors=advisors)


def get_advisor_account_details(request):
    token = request.cookies['token']
    # make sure manager is authorized
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    manager = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not manager:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
    userID = request.args.get('id')
    query = text("SELECT * from advisors where userID = :userID")
    result_cursor = db.session.execute(query, {'userID': userID})
    advisor = result_cursor.fetchone()
    # advisor = []
    # for row in rows:
    #     advisor.append(row._data)
    print(advisor.fullName)
    return render_template("manager/advisor/advisor-profile-details.html", manager=manager, advisor=advisor)


def accept_advisor_modifications(request):
    token = request.cookies['token']
    # make sure manager is authorized
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    manager = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not manager:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
    # get hidden form data
    advisorID = request.form['advisorID']
    # update advisor table with userID
    advisor_query = text("UPDATE advisors SET status = 'active' where advisorID = :advisorID")
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print(advisorID[0])
    advisor_cursor = db.session.execute(advisor_query, {'advisorID': advisorID})
    # commit changes to db
    db.session.commit()
    if not advisor_cursor:
        flash('Failed to approve advisor modification request', 'error')
        return redirect(url_for('manager.get_advisors_accounts_view', manager=manager))
    flash('Advisor modifications approved successfully', 'success')
    # get the user so we can send him the email
    user = db.session.execute(text("SELECT  email, fullName from advisors where advisorID = :advisorID"),
                              {"advisorID": advisorID}).fetchone()
    # send credentials to the trainee
    recipient = user[0]
    sender = manager["email"]
    message = """
        Dear {0},

        Your account modification has been approved, you can login now. 
        Best regards,
        {1} from TMS
                    """.format(user[1], manager["fullname"])
    subject = "Regarding Your Account Modification"
    response = helper.send_email(recipient=recipient, sender=sender, message=message, subject=subject)
    return redirect(url_for('manager.get_advisors_accounts_view', manager=manager))


def reject_advisor_modifications(request):
    token = request.cookies['token']
    # make sure manager is authorized
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    manager = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not manager:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
    # get hidden form data
    advisorID = request.form['advisorID']
    # update advisor table with userID
    advisor_query = text("UPDATE advisors SET status = 'active' where advisorID = :advisorID")
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print(advisorID[0])
    advisor_cursor = db.session.execute(advisor_query, {'advisorID': advisorID})
    # commit changes to db
    db.session.commit()
    result = advisor_cursor.rowcount
    if not result:
        flash('Failed to approve advisor modification request', 'error')
        return redirect(url_for('manager.get_advisors_accounts_view', manager=manager))
    flash('Advisor modifications rejected successfully', 'success')
    return redirect(url_for('manager.get_advisors_accounts_view', manager=manager))


"""
    This is the function that prepares the data for the view 'deactivate advisor account', 
    returns the view along with its data 

"""


def get_deactivate_advisors(request):
    # token is the manager record from the database
    token = request.cookies['token']
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    manager = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not manager:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
    query = text("SELECT * from advisors where status = 'inactive'")
    result_cursor = db.session.execute(query)
    rows = result_cursor.fetchall()
    advisors = []
    for row in rows:
        advisors.append(row._data)
    return render_template("manager/advisor/deactivate_advisor.html", manager=manager, advisors=advisors)


"""
    This is the controller function that handles the deactivate button in the deactivate advisors view
"""


def approve_advisor_deactivation(request):
    token = request.cookies['token']
    # make sure manager is authorized
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    manager = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not manager:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
    # get hidden form data
    advisorID = request.form['advisorID']
    # update advisor table with userID
    advisor_query = text("UPDATE advisors SET status = 'active' where advisorID = :advisorID")
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print(advisorID[0])
    advisor_cursor = db.session.execute(advisor_query, {'advisorID': advisorID})
    # commit changes to db
    db.session.commit()
    if not advisor_cursor:
        flash('Failed to deactivate advisor', 'error')
        return redirect(url_for('manager.get_deactivate_advisors_view'))
    flash('Advisor deactivated successfully', 'success')
    # get the user so we can send him the email
    user = db.session.execute(text("SELECT  email, fullName from advisors where advisorID = :advisorID"),
                              {"advisorID": advisorID}).fetchone()
    # send credentials to the trainee
    recipient = user[0]
    sender = manager["email"]
    message = """
            Dear {0},
            We're so sorry to see you leave. 
            Your account data is deleted, you can't login or retrieve the data. 


            Best regards,
            {1} from TMS
                        """.format(user[1], manager["fullname"])
    subject = "Regarding Your Account Deactivation"
    response = helper.send_email(recipient=recipient, sender=sender, message=message, subject=subject)

    return redirect(url_for('manager.get_deactivate_advisors_view'))


"""
    This is the controller function that handles the reject button in the deactivate advisors view
"""


def reject_advisor_deactivation(request):
    token = request.cookies['token']
    # make sure manager is authorized
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    manager = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not manager:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
    # get hidden form data
    advisorID = request.form['advisorID']
    # update advisor table with userID
    advisor_query = text("UPDATE advisors SET status = 'rejected' where advisorID = :advisorID")
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print(advisorID[0])
    advisor_cursor = db.session.execute(advisor_query, {'advisorID': advisorID})
    # commit changes to db
    db.session.commit()
    if not advisor_cursor:
        flash('Failed to reject advisor', 'error')
        return redirect(url_for('manager.get_deactivate_advisors_view'))
    flash('Advisor rejected successfully', 'success')
    return redirect(url_for('manager.get_deactivate_advisors_view'))
