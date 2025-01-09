from flask import request, render_template, jsonify, url_for, redirect, flash
from sqlalchemy import text
import helpers.token as token_helper
from app import db



"""
    gets all available programs, returns the view that displays all the programs alongside with this data
"""
def get_all_programs(request):
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
    query = text("SELECT * FROM training_programs")
    result_cursor = db.session.execute(query)
    rows = result_cursor.fetchall()
    programs = []
    for row in rows:
        programs.append(row._data)
    return render_template("manager/training-program/all_programs.html", manager=manager, programs=programs)


"""
    gets the view the has the add program form 
"""
def get_add_program(request):
    token = request.cookies['token']
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    manager = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not manager:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
    # must prepare areas so that it could be a drop-down list
    areas = ['Software Development','Healthcare','Machine Learning','Network Security','Data Warehousing','Digital Marketing','Renewable Energy','Graphic Design','Pastry and Baking']
    return render_template('manager/training-program/add_program.html', manager=manager, areas=areas)


"""
    handles the action of the add program form 
"""
def handle_add_program(request):
    token = request.cookies['token']
    # verify manager
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    manager = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not manager:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
    name = request.form['programName']
    description = request.form['description']
    area = request.form['area']
    fees = request.form['fees']
    start = request.form['start']
    end = request.form['end']
    query = text("""INSERT INTO `training_programs` 
                (`name`, `description`, `area_of_training`, `fees`, `start_date`, `end_date`) 
        VALUES  (:name, :description, :area, :fees, :start, :end)""")
    data = {'name':name, 'description':description, 'area':area, 'fees':fees, 'start':start, 'end':end}
    cursor = db.session.execute(query, data)
    db.session.commit()
    result = cursor.rowcount
    if not result:   
        flash('Failed to add program', 'error')
        return redirect(url_for('manager.get_all_programs_view', manager=manager))
    flash('Program added successfully', 'success')
    return redirect(url_for('manager.get_all_programs_view', manager=manager))


"""
    gets the view that has the edit program form, where this form inputs are already filled in with the program data 
"""
def get_edit_program(request):
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
    programID = request.args.get('id')
    areas = ['Software Development','Healthcare','Machine Learning','Network Security','Data Warehousing','Digital Marketing','Renewable Energy','Graphic Design','Pastry and Baking']
    query = text("SELECT * from training_programs where programID = :programID")
    # area_of_training_query = text("SELECT * from training_programs where area_of_training=0")
    program_cursor = db.session.execute(query, {'programID':programID})
    program = program_cursor.fetchone()

    return render_template('manager/training-program/update_program.html', areas=areas, manager=manager, program=program)


"""
    handles the action of the edit program form
"""
def handle_edit_program(request):
    token = request.cookies['token']
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    manager = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not manager:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
    programID = request.form['programID']
    name = request.form['programName']
    description = request.form['description']
    area = request.form['area']
    fees = request.form['fees']
    start = request.form['start']
    end = request.form['end']
    query = text("""UPDATE training_programs SET 
    `name` = :name, `description` = :description, `area_of_training` = :area, `fees` = :fees, `start_date` = :start, `end_date` = :end 
    WHERE `programID` = :programID""")
    data = {'programID':programID, 'name':name, 'description':description, 'area':area, 'fees':fees, 'start':start, 'end':end}
    cursor = db.session.execute(query, data)
    db.session.commit()
    result = cursor.rowcount
    if not result:
        flash('Failed to edit program', 'error')
        return redirect(url_for('manager.get_all_programs_view'))
    flash('Program edited successfully', 'success')
    return redirect(url_for('manager.get_all_programs_view'))


"""
    handles the action of the delete program form
"""
def handle_delete_program(request):
    token = request.cookies['token']
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    manager = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not manager:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
    programID = request.form['programID']
    query = text("DELETE FROM training_programs WHERE programID=:programID")
    cursor = db.session.execute(query, {'programID':programID})
    db.session.commit()
    result = cursor.rowcount

    if not result:   
        flash('Failed to Delete program', 'error')
        return redirect(url_for('manager.get_all_programs_view'))
    flash('Program deleted successfully', 'success')
    return redirect(url_for('manager.get_all_programs_view'))

