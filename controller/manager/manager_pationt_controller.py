from flask import redirect, url_for, request, render_template, jsonify, flash
from sqlalchemy import text
from app import db
import helpers.token as token_helper
import secrets
from helpers import helper as helper

"""
    This is the function that prepares data for the 'pending trainees' view, and returns the view with its data 
"""


def get_pending_trainees(request):
    token = request.cookies['token']
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    manager = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not manager:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
    # token is the manager id or the manager record
    query = text("SELECT * from trainees where status = 'pending'")
    result_cursor = db.session.execute(query)
    rows = result_cursor.fetchall()
    trainees = []
    for row in rows:
        trainees.append(row._data)
    return render_template("manager/trainee/pending_trainees.html", manager=manager, trainees=trainees)


"""
    This is the controller function that handles the approve button in the pending trainees view
    it's actually not yet implemented or linked to its view
"""


def approve_trainee_registration(request):
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
    traineeID = request.form['traineeID']
    traineeEmail = request.form['traineeEmail']
    pass_length = 7
    # secret is python module that generates passwords according to ur prefered length
    password = secrets.token_urlsafe(pass_length)
    # insert trainee to user table first to link it to trainee table using userID(PK->FK relationship)
    user_query = text("INSERT INTO users (password, email, classification) VALUES (:password, :email, 'trainee')")
    user_cursor = db.session.execute(user_query, {'password': password, 'email': traineeEmail})
    db.session.commit()
    if not user_cursor:
        return jsonify('the problem is in insert to users')
        flash('Failed to approve trainee', 'error')
        return redirect(url_for('manager.get_pending_trainees_view'))
    # get userID from previous query
    userID = user_cursor.lastrowid
    # update trainee table with userID
    trainee_query = text("UPDATE trainees SET status = 'active', userID = :userID  WHERE traineeID = :traineeID")
    trainee_cursor = db.session.execute(trainee_query, {'userID': userID, 'traineeID': traineeID})
    trainee_rows = trainee_cursor.rowcount
    db.session.commit()
    if not trainee_rows:
        # return jsonify('the problem is in update trainees', userID)
        flash('Failed to approve trainee', 'error')
        return redirect(url_for('manager.get_pending_trainees_view'))
    flash('Trainee approved successfully', 'success')
    # get the user so we can send him his data
    user = db.session.execute(text("SELECT password, email from users where userID = :userID"),
                              {"userID": userID}).fetchone()
    # send credentials to the trainee
    recipient = user[1]
    sender = manager["email"]
    message = """
    Dear trainee,

Welcome! We're delighted to have you join our system.

As a valued member, we're here to support you every step of the way. If you have any questions or need assistance, don't hesitate to reach out to our friendly support team.

Let's embark on this exciting journey together!
Here are your login credentials, Don't share them with anyone
Email: {0}
Password: {1}
Note: you can change your information anytime. 


Best regards,
{2} from TMS.
    """.format(user[1], user[0], manager["fullname"])
    subject = "Welcome to TMS!"
    response = helper.send_email(recipient=recipient, sender=sender, message=message, subject=subject)

    return redirect(url_for('manager.get_pending_trainees_view'))


"""
    This is the controller function that handles the reject button in the pending trainees view
"""


def reject_trainee_registration(request):
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
    traineeID = request.form['traineeID']
    # update trainee table with userID
    trainee_query = text("UPDATE trainees SET status = 'rejected' WHERE traineeID = :traineeID")
    trainee_cursor = db.session.execute(trainee_query, {'traineeID': traineeID})
    trainee_rows = trainee_cursor.rowcount
    # commit changes to db
    db.session.commit()
    if not trainee_rows:
        flash('Failed to approve trainee', 'error')
        return redirect(url_for('manager.get_pending_trainees_view'))
    flash('Trainee rejected successfully', 'success')
    # get the user so we can send him his data
    user = db.session.execute(text("SELECT  email, fullName from trainees where traineeID = :traineeID"),
                              {"traineeID": traineeID}).fetchone()
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
    return redirect(url_for('manager.get_pending_trainees_view'))


def get_training_requests_view(request):
    token = request.cookies['token']
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    manager = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not manager:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
    # token is the manager id or the manager record
    request_query = text("SELECT * from training_registration where status = 'pending'")
    advisor_query = text("SELECT advisorID, username from advisors where status='active'")
    result_cursor = db.session.execute(request_query)
    advisor_cursor = db.session.execute(advisor_query)
    request_rows = result_cursor.fetchall()
    advisor_rows = advisor_cursor.fetchall()

    advisor = []
    requests = []
    for row in request_rows:
        requests.append(row._data)
    for row in advisor_rows:
        advisor.append(row._data)
    return render_template("manager/trainee/pending_requests.html", manager=manager, requests=requests, advisor=advisor)


def approve_training_request(request):
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
    requestID = request.form['requestID']
    advisorID = request.form['advisorID']
    traineeID = request.form['traineeID']
    # update trainee and training_registration table with status
    request_query = text(
        "UPDATE training_registration SET status = 'approved', advisorID=:advisorID where ID = :requestID")
    trainee_query = text("UPDATE trainees SET status = 'on_training' where traineeID = :traineeID")
    balance_query = text(
        "INSERT INTO balance_sheet (traineeID, type, amount, transaction_time) VALUES (:traineeID, 'Credit', 100.0, NOW())")
    request_cursor = db.session.execute(request_query, {'requestID': requestID, 'advisorID': advisorID})
    trainee_cursor = db.session.execute(trainee_query, {'traineeID': traineeID})
    balance_cursor = db.session.execute(balance_query, {'traineeID': traineeID})
    # commit changes to db
    db.session.commit()
    if not request_cursor and not trainee_cursor and not balance_cursor:
        flash('Failed to approve trainee training request', 'error')
        return redirect(url_for('manager.get_training_requests'))
    flash('Trainee training request approved successfully', 'success')
    # inform advisor
    advisor = db.session.execute(text("SELECT  email, fullName from advisors where advisorID = :advisorID"),
                                 {"advisorID": advisorID}).fetchone()
    # get the trainee so we can send him the email
    trainee = db.session.execute(text("SELECT  email, fullName from trainees where traineeID = :traineeID"),
                                 {"traineeID": traineeID}).fetchone()

    # inform advisor
    recipient = advisor[0]
    sender = manager["email"]
    message = """
    Dear {0},
        The following trainee has been assigned to you
        Trainee Information:
            Trainee ID: {1}
            Trainee Name: {2}
            Trainee Email: {3}
            Training Registration ID: {4}

    Best regards,
    {5} from TMS
                """.format(advisor[1], traineeID, trainee[1], trainee[0], requestID, manager["fullname"])
    subject = "New Trainee has been assigned"
    response1 = helper.send_email(recipient=recipient, sender=sender, message=message, subject=subject)

    # get the training registration data so we can send him his data
    program = db.session.execute(text("""
        SELECT p.`name`, p.`fees`,p.`start_date`, p.`end_date` 
        from `training_registration` r JOIN `training_programs` p on p.`programID` = r.`training_program_id`
        WHERE r.`ID` = :requestID 
    """), {"requestID":requestID}).fetchone()
    # send credentials to the trainee
    recipient = trainee[0]
    sender = manager["email"]
    message = """
Dear {0},

Congratulations! We are thrilled to inform you that your training application has been approved. We believe this training will be a valuable opportunity for you to enhance your skills and knowledge in [Training Program/Subject].

Here are the details you need to know:

Training Program: {1}
Start Date: {2}
End Date: {3}
Fees: {4}

Please make sure to mark your calendar and be prepared to make the most out of this enriching experience. If you have any further questions or require additional information, feel free to reach out to our dedicated training team.

Once again, congratulations on being selected for this training program. We look forward to seeing you there and witnessing your growth.

Best regards,
{5} from TMS
            """.format(trainee[1], program[0], program[1], program[2], program[3], manager["fullname"])
    subject = "Congratulations! Your Training Application has been Approved"
    response2 = helper.send_email(recipient=recipient, sender=sender, message=message, subject=subject)
    return redirect(url_for('manager.get_training_requests'))


def reject_training_request(request):
    # print("inside reject")
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
    requestID = request.form['requestID']
    # update trainee table with userID
    request_query = text("UPDATE training_registration SET status = 'rejected' where ID = :requestID")
    request_cursor = db.session.execute(request_query, {'requestID': requestID})
    # commit changes to db
    db.session.commit()
    if not request_cursor:
        flash('Failed to reject training request', 'error')
        return redirect(url_for('manager.get_training_requests'))
    flash('Trainee training request rejected successfully', 'success')

    # get the user so we can send him his data
    user = db.session.execute(text(
        "SELECT  t.`email`, t.`fullName` from `trainees` t join `training_registration` r on t.`traineeID` = r.`traineeID` where r.`ID` = :requestID"),
        {"requestID": requestID}).fetchone()
    # send credentials to the trainee
    recipient = user[0]
    sender = manager["email"]
    message = """
    Dear {0},

    We regret to inform you that your training application has not been approved at this time. Thank you for your interest.


    Best regards,
    {1} from TMS
            """.format(user[1], manager["fullname"])
    subject = "Regarding Your Training Application"
    response = helper.send_email(recipient=recipient, sender=sender, message=message, subject=subject)
    return redirect(url_for('manager.get_training_requests'))


def get_trainee_account(request):
    token = request.cookies['token']
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    manager = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not manager:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
    # token is the manager id or the manager record
    query = text("SELECT * from trainees where status = 'in_review'")
    result_cursor = db.session.execute(query)
    rows = result_cursor.fetchall()
    trainees = []
    for row in rows:
        trainees.append(row._data)
    return render_template("manager/trainee/trainee_account_modification.html", manager=manager, trainees=trainees)


def get_trainee_account_details(request):
    token = request.cookies['token']
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    manager = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not manager:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
    userID = request.args.get('id')
    query = text("SELECT * from trainees where userID = :userID")
    result_cursor = db.session.execute(query, {'userID': userID})
    trainee = result_cursor.fetchone()
    return render_template("manager/trainee/trainee-profile-details.html", trainee=trainee, manager=manager)


def accept_trainee_modifications(request):
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
    traineeID = request.form['traineeID']
    # update trainee table with userID
    trainee_query = text("UPDATE trainees SET status = 'active' where traineeID = :traineeID")
    trainee_cursor = db.session.execute(trainee_query, {'traineeID': traineeID})
    # commit changes to db
    db.session.commit()
    if not trainee_cursor:
        flash('Failed to approve trainee modification request', 'error')
        return redirect(url_for('manager.get_trainees_accounts_view'))
    flash('Trainee modifications approved successfully', 'success')
    # get the user so we can send him the email
    user = db.session.execute(text("SELECT  email, fullName from trainees where traineeID = :traineeID"),
                              {"traineeID": traineeID}).fetchone()
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
    return redirect(url_for('manager.get_trainees_accounts_view'))


def reject_trainee_modifications(request):
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
    traineeID = request.form['traineeID']
    # update trainee table with userID
    trainee_query = text("UPDATE trainees SET status = 'active' where traineeID = :traineeID")

    trainee_cursor = db.session.execute(trainee_query, {'traineeID': traineeID})
    # commit changes to db
    result = db.session.commit()
    if not result:
        flash('Failed to approve trainee modification request', 'error')
        return redirect(url_for('manager.get_trainees_accounts_view'))
    flash('Trainee modifications rejected successfully', 'success')

    return redirect(url_for('manager.get_trainees_accounts_view'))


"""
    This is the function that prepares the data for the view 'deactivate trainee account', 
    returns the view along with its data 

"""


def get_deactivate_trainees(request):
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
    # token is the manager id or the manager record
    query = text("SELECT * from trainees where status = 'inactive'")
    result_cursor = db.session.execute(query)
    rows = result_cursor.fetchall()
    trainees = []
    for row in rows:
        trainees.append(row._data)
    # implement the query so that you get the trainees deactivation requests
    # i think we are supposed to implement something in the database for it

    return render_template("manager/trainee/deactivate_trainee.html", manager=manager, trainees=trainees)


"""
    This is the controller function that handles the deactivate button in the deactivate trainees view
    it's actually not yet implemented or linked to its view
"""


def approve_trainee_deactivation(request):
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
    traineeID = request.form['traineeID']
    # update trainee table with userID
    trainee_query = text("UPDATE trainees SET status = 'rejected' where traineeID = :traineeID")
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print(traineeID[0])
    trainee_cursor = db.session.execute(trainee_query, {'traineeID': traineeID})
    # commit changes to db
    db.session.commit()
    if not trainee_cursor:
        flash('Failed to deactivate trainee', 'error')
        return redirect(url_for('manager.get_deactivate_trainees_view'))
    flash('Trainee deactivated successfully', 'success')
    # get the user so we can send him the email
    user = db.session.execute(text("SELECT  email, fullName from trainees where traineeID = :traineeID"),{"traineeID": traineeID}).fetchone()
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
    return redirect(url_for('manager.get_deactivate_trainees_view'))


"""
    This is the controller function that handles the reject button in the deactivate trainees view
    it's actually not yet implemented or linked to its view
"""


def reject_trainee_deactivation(request):
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
    traineeID = request.form['traineeID']
    # update trainee table with userID
    trainee_query = text("UPDATE trainees SET status = 'active' where traineeID = :traineeID")
    trainee_cursor = db.session.execute(trainee_query, {'traineeID': traineeID})
    # commit changes to db
    db.session.commit()
    if not trainee_cursor:
        flash('Failed to reject trainee', 'error')
        return redirect(url_for('manager.get_deactivate_trainees_view'))
    flash('Trainee rejected successfully', 'success')
    return redirect(url_for('manager.get_deactivate_trainees_view'))
