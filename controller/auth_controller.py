from flask import render_template, jsonify, redirect, url_for, flash
from sqlalchemy import text
import helpers.token as tokenHelper
from app import app
from app import db


def login_view():
    return render_template('login.html')


def handle_login(request):
    # get information from request
    email = request.form['email']
    password = request.form['password']
    if not email or not password:
        flash('Missing email or password', 'error')
        return redirect(url_for('auth.login_view'))
    # let's look whether we can find those credentials
    query = text("SELECT * from users where email = :email and password = :password")
    params = {"email": email, "password": password}
    result = db.session().execute(query, params)
    row = result.fetchone()
    # return jsonify('querying trainee returned nothing')
    # print(row)
    if not row:
        return jsonify("nothing");
        flash('Email or password are incorrect, please try again', 'error')
        return redirect(url_for('auth.login_view'))
    # NOTE: We need to check the statuses of the trainee and the advisor before authorizing them to the system
    # Which means we'll fetch the trainee and advisor records
    # which also means deleting the trainee, advisor helpers :))))))
    classification = row[3]
    # print(classification)
    if classification == "manager":
        # get the row from the database
        manager_record = db.session.execute(text(
            "SELECT * from managers where userID = :userID"),
            {"userID": row[0]}
        ).fetchone()
        manager = {
            "managerID": manager_record[0],
            "username": manager_record[1],
            "fullname": manager_record[2],
            "email": manager_record[3],
            "userID": manager_record[4],
        }
        # generate token
        token = tokenHelper.generate_token(manager)
        # print("inside manager")
        response = redirect(url_for('manager.dashboard_view'))
        response.set_cookie('token', token)
        return response
    elif classification == "advisor":
        # get the row from the database
        advisor_record = db.session.execute(
            text("SELECT * from advisors where userID = :userID and status in ('active','training')"),
            {"userID": row[0]}
        ).fetchone()
        if not advisor_record:
            # it means the satuts match failed, so the user can not be authorized
            flash("you are not authorized to the system.")
            return redirect(url_for('auth.login_view'))
        advisor = {
            "advisorID": advisor_record[0],
            "username": advisor_record[1],
            "fullname": advisor_record[2],
            "email": advisor_record[3],
            "discipline": advisor_record[4],
            "status": advisor_record[5],
            "userID": advisor_record[6],
        }
        # generate token
        token = tokenHelper.generate_token(advisor)
        # print("inside manager")
        response = redirect(url_for('advisor.dashboard_view'))
        response.set_cookie('token', token)
        return response
    elif classification == "trainee":
        # get the row from the database
        trainee_record = db.session.execute(
            text("SELECT * from trainees where userID = :userID and status in ('active','on_training')"),
            {"userID": row[0]}
        ).fetchone()
        if not trainee_record:
            # it means the satuts match failed, so the user can not be authorized
            flash("you are not authorized to the system yet, wait for admin approval")
            return redirect(url_for('auth.login_view'))

        trainee = {
            "traineeID": trainee_record[0],
            "username": trainee_record[1],
            "fullname": trainee_record[2],
            "email": trainee_record[3],
            "desired_field": trainee_record[4],
            "area_of_training": trainee_record[5],
            "status": trainee_record[6],
            "balance": trainee_record[7],
            "training_materials": trainee_record[8],
            "userID": trainee_record[9],
        }
        # generate token
        token = tokenHelper.generate_token(trainee)
        # print("inside trainee")
        response = redirect(url_for('trainee.dashboard_view'))
        response.set_cookie('token', token)
        return response
    else:
        flash('Email or password is wrong', 'error')
        return redirect(url_for('auth.login_view'))


def signup_view(request):
    classification = request.args.get('classification')
    if classification == "advisor":
        return render_template('registration/advisor_register.html')
    elif classification == "trainee":
        return render_template('registration/trainee_register.html')
    # If the classification field is somehow tampered, this shows the red flag
    # this case is handled in the auth.signup endpoint, no need to handle it here


def handle_trainee_signup(request):
    username = request.form['username']
    fullname = request.form['fullname']
    email = request.form['email']
    desiredField = request.form['desiredField']
    area = request.form['area']
    # TODO: upload required materials to the user-uploads directory
    if not username or not email or not desiredField or not area:
        flash('signup information is missing', 'error')
        return redirect(url_for('auth.signup_view?classification=trainee'))
    query = text(
        """
        INSERT INTO `trainees` (username, fullname, email, desired_field, area_of_training) VALUES (:username,:fullname, :email, :desired_field, :area)""")
    params = {'username': username, 'fullname': fullname, 'email': email, 'desired_field': desiredField, 'area': area}
    result = db.session.execute(query, params)
    if not result:
        flash('failed to add data', 'error')
        return redirect(url_for('auth.signup_view?classification=trainee'))
    # in case of the first query success, this shall be a pending trainee request waiting for the manager approval
    else:
        flash('Successfully added your information, wait for our email')
        db.session.commit()
        return redirect(url_for('auth.login_view'))


def handle_advisor_signup(request):
    username = request.form['username']
    fullname = request.form['fullname']
    email = request.form['email']
    discipline = request.form['discipline']
    # TODO: upload required materials to the user-uploads directory
    if not username or not email or not fullname or not discipline:
        flash('signup information is missing', 'error')
        return redirect(url_for('auth.signup_view?classification=trainee'))

    query = text(
        """
        INSERT INTO advisors (username, fullname, email, discipline) VALUES (:username,:fullname, :email, :discipline)""")
    params = {'username': username, 'fullname': fullname, 'email': email, 'discipline': discipline}
    result = db.session.execute(query, params)
    if not result:
        flash('failed to add data', 'error')
        return redirect(url_for('auth.signup_view?classification=advisor'))
    # in case of the first query success, this shall be a pending trainee request waiting for the manager approval
    else:
        flash('Successfully added your information, wait for our email')
        db.session.commit()
        return redirect(url_for('auth.login_view'))


def signout(request):
    response = redirect(url_for('auth.login_view'))
    response.set_cookie('token', '')
    #    return jsonify(var)
    #   return jsonify(response.headers['Cookie'])
    return response
