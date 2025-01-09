from flask import Blueprint, request
from controller.manager import manager_trainee_controller, manager_controller, manager_advisor_controller, manager_programs_controller

manager_blueprint = Blueprint("manager", __name__)


@manager_blueprint.route('/manager', methods=["GET"])
def dashboard_view():
    return manager_controller.index(request)


# Manager-pationt Routes
@manager_blueprint.route('/pationt/pending', methods=["GET"])
def get_pending_pationt_view():
    return manager_pationt_controller.get_pending_pationt(request)


@manager_blueprint.route('/approve/pationt/', methods=["POST"])
def approve_pationt():
    return manager_pationt_controller.approve_pationt_registration(request)


@manager_blueprint.route('/reject/pationt/', methods=["POST"])
def reject_pationt():
    return manager_pationt_controller.reject_pationt_registration(request)


@manager_blueprint.route('/tpationt/requests', methods=["GET"])
def get_pationt_requests():
    return manager_pationt_controller.get_pationt_requests_view(request)


@manager_blueprint.route('/pationt/requests/approve', methods=["POST"])
def approve_pationt_requests():
    return manager_pationt_controller.approve_pationt_request(request)


@manager_blueprint.route('/tpationt/requests/reject', methods=["POST"])
def reject_pationt_requests():
    return manager_pationt_controller.reject_pationt_request(request)


@manager_blueprint.route('/pationt/deactivate/all', methods=["GET"])
def get_deactivate_pationt_view():
    return manager_pationt_controller.get_deactivate_pationt(request)


@manager_blueprint.route('/pationt/deactivate', methods=["POST"])
def deactivate_pationt():
    return manager_pationt_controller.approve_pationt_deactivation(request)


@manager_blueprint.route('/pationt/reject/deactivate', methods=["POST"])
def reject_deactivate_pationt():
    return manager_pationt_controller.reject_pationt_deactivation(request)


@manager_blueprint.route('/pationt/account', methods=["GET"])
def get_pationt_accounts_view():
    return manager_pationt_controller.get_pationt_account(request)


@manager_blueprint.route('/pationt/account/details', methods=["GET"])
def get_pationt_accounts_details_view():
    return manager_pationt_controller.get_pationt_account_details(request)


@manager_blueprint.route('/pationt/approve/modifications', methods=["POST"])
def accept_pationt_modification():
    return manager_pationt_controller.accept_pationt_modifications(request)


@manager_blueprint.route('/pationt/reject/modifications', methods=["POST"])
def reject_pationt_modification():
    return manager_pationt_controller.reject_pationt_modifications(request)


# Manager-dector Routes


@manager_blueprint.route('/dector/pending', methods=["GET"])
def get_pending_dector_view():
    return manager_dector_controller.get_pending_dector(request)


@manager_blueprint.route('/approve/dector', methods=["POST"])
def approve_dector():
    return manager_dector_controller.approve_dectors_registration(request)


@manager_blueprint.route('/reject/dector', methods=["POST"])
def reject_dector():
    return manager_dector_controller.reject_dectors_registration(request)


@manager_blueprint.route('/dectors/account', methods=["GET"])
def get_dectors_accounts_view():
    return manager_dector_controller.get_dector_account(request)


@manager_blueprint.route('/dectors/account/details', methods=["GET"])
def get_dectors_accounts_details_view():
    return manager_dector_controller.get_dector_account_details(request)


@manager_blueprint.route('/dectors/approve/modifications', methods=["POST"])
def accept_dector_modification():
    return manager_dector_controller.accept_dector_modifications(request)


@manager_blueprint.route('/dectors/account/details', methods=["POST"])
def reject_dector_modification():
    return manager_dector_controller.reject_dector_modifications(request)


@manager_blueprint.route('/dectors/deactivate/all', methods=["GET"])
def get_deactivate_dectors_view():
    return manager_dector_controller.get_deactivate_dectors(request)


@manager_blueprint.route('/dector/deactivate', methods=["POST"])
def deactivate_dector():
    return manager_dector_controller.approve_dector_deactivation(request)


@manager_blueprint.route('/dector/reject/deactivate', methods=["POST"])
def reject_deactivate_dector():
    return manager_dector_controller.reject_dector_deactivation(request)

# Progam Routes

@manager_blueprint.route('/programs', methods=["GET"])
def get_all_programs_view():
    return manager_programs_controller.get_all_programs(request)


@manager_blueprint.route('/programs/create/form', methods=["GET"])
def get_add_program_view():
    return manager_programs_controller.get_add_program(request)


@manager_blueprint.route('/program/create', methods=["POST"])
def add_program():
    return manager_programs_controller.handle_add_program(request)


@manager_blueprint.route('/programs/edit', methods=["GET"])
def get_edit_program_view():
    return manager_programs_controller.get_edit_program(request)


@manager_blueprint.route('/programs/edit/save', methods=["POST"])
def edit_program():
    return manager_programs_controller.handle_edit_program(request)


@manager_blueprint.route('/program/delete', methods=["POST"])
def delete_program():
    return manager_programs_controller.handle_delete_program(request)

# Manager - Billing
@manager_blueprint.route('/billing', methods=["GET"])
def get_balance_sheet_view():
    return manager_controller.get_balance_sheet(request)



# Manager - Emailing
@manager_blueprint.route('/email/create', methods=["GET"])
def get_email_form():
    return manager_controller.get_email_form(request)


@manager_blueprint.route('/email/send', methods=["POST"])
def send_email():
    return manager_controller.send_email(request)



# Manager - System Log
@manager_blueprint.route('/systemlog', methods=["GET"])
def get_system_log():
    return manager_controller.get_system_log(request)
