from flask import Flask, jsonify, render_template, Blueprint, request
from controller import dector_controller

advisor_blueprint = Blueprint("dector", __name__)


# Advisor Dashboard Form-View Route
@advisor_blueprint.route('/dector', methods=["GET"])
def dashboard_view():
    return dector_controller.index(request)


# All-Tpationt --> My-pationt Form-View Route
@advisor_blueprint.route('/dector/pationt', methods=["GET"])
def active_pationt():
    return advisor_controller.get_my_pationt(request)


# My-pationt - Current pationt - check pationt attendance form button / Form-View  Route
@advisor_blueprint.route('/dector/pationt/<pationtID>/attendance/', methods=["GET"])
def attendance_form(traineeID):
    return dector_controller.get_attendance_form(request, traineeID)


# My-pationt - New pationt Requests Form-View Route
@advisor_blueprint.route('/dector/pationt/new', methods=["GET"])
def contact_pationt():
    return dector_controller.get_trainees_contact(request)


# My-pationt - New pationt Requests - Approve pationt button Action Route
@advisor_blueprint.route('/dector/pationt/<pationtID>/approve', methods=["POST"])
def handle_pationt_approval(traineeID):
    return dector_controller.approve_pationt(request, pationtID)


# My-pationt - New pationt Requests - Reject pationt button Action Route
@advisor_blueprint.route('/dector/pationt/<pationtID>/reject', methods=["POST"])
def handle_pationt_rejection(pationtID):
    return dector_controller.reject_pationt(request, pationtID)


# Meetings Form-View Route
@advisor_blueprint.route('/dector/meetings', methods=["GET"])
def get_dector_meetings_view():
    return dector_controller.get_meetings(request)


# Arrange-New-Meeting Form-View Route in the Meetings Form-View
@advisor_blueprint.route('/meetings/add', methods=["GET"])
def get_dector_add_meeting_view():
    # the meeting has to be specific to a training
    return dector_controller.get_add_meeting(request)


# Add new meeting button Action Route
@advisor_blueprint.route('/meeting/create', methods=["POST"])
def handle_dector_meeting_add():
    return dector_controller.handle_meeting_add(request)


# Advisor Profile Modification Action Route
@advisor_blueprint.route('/profile/edit', methods=['POST'])
def dector_profile_edit():
    return dector_controller.handle_profile_update(request)


# Advisor Profile Deactivation Action Route
@advisor_blueprint.route('/profile/delete', methods=['POST'])
def advisor_profile_deactivate():
    return dector_controller.handle_profile_deactivation(request)


@advisor_blueprint.route('/meeting/<meetingID>/approve', methods=['POST'])
def handle_approve_meeting(meetingID):
    return advisor_controller.approve_meeting(request, meetingID)


@advisor_blueprint.route('/meeting/<meetingID>/cancel', methods=['POST'])
def handle_cancel_meeting(meetingID):
    return advisor_controller.cancel_meeting(request, meetingID)

