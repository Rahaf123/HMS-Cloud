from flask import Flask, Blueprint, render_template, url_for, redirect, request, flash
from controller import auth_controller

auth_blueprint = Blueprint("auth", __name__)

# to make sure nothing goes wrong
@auth_blueprint.route('/', methods=['GET'])
def home():
    return redirect(url_for('auth.login_view'))

# this is the route that returns the login form view
@auth_blueprint.route('/login', methods=['GET'])
def login_view():
    return auth_controller.login_view()


# this is the route that handles the login request
@auth_blueprint.route('/auth/login', methods=['POST'])
def login():
    return auth_controller.handle_login(request)


# this is the route that returns the signup form view
@auth_blueprint.route('/signup', methods=['GET'])
def signup_view():
    return auth_controller.signup_view(request)


# this is the route that handles the signup request
@auth_blueprint.route('/auth/signup', methods=['POST'])
def signup():
    classification = request.form['classification']
    if classification == 'trainee':
        return auth_controller.handle_trainee_signup(request)
    elif classification == 'advisor':
        return auth_controller.handle_advisor_signup(request)
    else:
        flash('Something is not right', 'error')
        return redirect(url_for('auth.login_view'))

# signout route
@auth_blueprint.route('/signout', methods=['GET'])
def signout():
    return auth_controller.signout(request)



