from flask import render_template, flash, redirect, url_for, jsonify
from sqlalchemy import text
import helpers.token as token_helper
import helpers.helper as helper
from app import db


def index(request):
    # from token, fetch advisor id, then fetch the record from the database
    token = request.cookies['token']
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    advisor = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not advisor:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
        # If, however, the query returned the row -> render the dashboard
    return render_template('advisor/index.html', advisor=advisor)


def get_my_trainees(request):
    # from token, fetch advisor id, then fetch the record from the database
    token = request.cookies['token']
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    advisor = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not advisor:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
        # If, however, the query returned the row -> render the dashboard

    # select all registration process where the advisor ID is my ID
    # join that with the trainee table
    # return the result
    trainees = db.session.execute(
        text("""
                SELECT t.`traineeID`, t.`username`, t.`fullName`, t.`email`, t.`desired_field`, t.`area_of_training`, t.`status`, t.`training_materials`
                from `training_registration` r join `trainees` t on r.`traineeID` = t.`traineeID`
                where r.`status` = 'approved'
                GROUP BY r.`advisorID` 
                HAVING r.`advisorID` = :advisorID
                
            """),
        {"advisorID": advisor["advisorID"]}
    ).fetchall()
    if not trainees:
        flash("No trainees to display", 'error')
        return render_template('advisor/current-trainees.html', trainees=[], advisor=advisor)
    else:
        return render_template('advisor/current-trainees.html', trainees=trainees, advisor=advisor)


def get_trainees_contact(request):
    # get all trainess that their status is pending, registration is approved
    # from token, fetch advisor id, then fetch the record from the database
    token = request.cookies['token']
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    advisor = token_helper.verify_token(token)
    # if the query returned nothing -> it actually means we can't render the dashboard
    if not advisor:
        flash('Invalid token', 'error')
        return redirect(url_for('auth.login_view'))
        # If, however, the query returned the row -> render the dashboard

    # select all registration process where the advisor ID is my ID
    # join that with the trainee table
    # return the result
    trainees = db.session.execute(
        text("""
                    SELECT t.`traineeID`, t.`username`, t.`fullName`, t.`email`, t.`desired_field`, t.`area_of_training`, t.`status`, t.`training_materials`
                    from `training_registration` r join `trainees` t on r.`traineeID` = t.`traineeID`
                    where r.`status` = 'approved' and t.`status` = 'pending'
                    GROUP BY r.`advisorID` 
                    HAVING r.`advisorID` = :advisorID

                """),
        {"advisorID": advisor["advisorID"]}
    ).fetchall()
    if not trainees:
        flash("No trainees to display", 'error')
        return render_template('advisor/new-trainees-requests.html', trainees=[], advisor=advisor)
    else:
        return render_template('advisor/new-trainees-requests.html', trainees=trainees, advisor=advisor)


# handles the get attendance form for trainee button
def get_attendance_form(request, traineeID):
    # from the request, we'll fetch the hashed user_id (trainee)
    token = request.cookies['token']
    advisor = token_helper.verify_token(token)
    if not advisor:
        flash("Invalid token", 'error')
        return redirect(url_for('auth.login_view'))
    # TODO: I should actually check for the registration ID existence
    registration_record = db.session.execute(
        text("""
            SELECT * from `training_registration` where `traineeID` = :traineeID and `status`='approved'
        """),
        {"traineeID": traineeID}
    ).fetchone()
    if not registration_record:
        flash("Trainee has not registered")
        return redirect(request.referrer)
    else:
        # from the attendance_records, we'll select all records that belong to a specific registration_id
        # I think this is a list of records objects
        attendance_records = db.session.execute(
            text("""
                    SELECT * 
                    from attendance_records 
                    WHERE training_programID = :registration_id 
                """), {
                "registration_id": registration_record[0]
            }
        ).fetchall()
        if not attendance_records:
            flash("No records found")
            return render_template('advisor/attendance-form.html', advisor=advisor, attendance_records=[])
        else:
            return render_template('advisor/attendance-form.html', advisor=advisor,
                                   attendance_records=attendance_records)


def get_training_material(request):
    # from the request, we'll fetch the hashed user_id (trainee)
    token = request.cookies['token']
    advisor = token_helper.verify_token(token)
    if not advisor:
        flash("Invalid token", 'error')
        return redirect(url_for('auth.login_view'))
    return render_template('advisor/training-program.html', advisor=advisor, programs=[])


# handles the send email to trainee button
def approve_trainne(request, traineeID):
    return jsonify("inside approve trainee action")


def reject_trainee(request, traineeID):
    return jsonify("inside reject trainee action")


def get_meetings(request):
    # get the user id from the token in the request
    # ensure token existence
    # from the request, we'll fetch the hashed user_id (trainee)
    token = request.cookies['token']
    advisor = token_helper.verify_token(token)
    if not advisor:
        flash("Invalid token", 'error')
        return redirect(url_for('auth.login_view'))
    registration_records = db.session.execute(
        text(
            """
            SELECT * from `training_registration` where `advisorID` = :advisorID and `status`='approved'
            """
        ), {
            "advisorID": advisor["advisorID"]
        }
    ).fetchall()
    if not registration_records:
        flash("Inconsistency btw")
        return redirect(request.referrer)
    else:
        # all registration processes that belong to that advisor.
        registration_ids = []
        for record in registration_records:
            registration_ids.append(record[0]);
        # return jsonify(registration_ids)
        # select * from meetings using registration id
        meetings = db.session.execute(
            text("""
                        SELECT * from `meetings` where `registration_id` IN :registration_ids
                    """),
            {
                "registration_ids": registration_ids
            }).fetchall()
        if not meetings:
            flash("No meetings yet")
            return render_template('advisor/advisor-meetings.html', advisor=advisor, meetings=[])
        else:
            return render_template('advisor/advisor-meetings.html', advisor=advisor, meetings=meetings)


"""
    This function renders the add new meeting form
"""


def get_add_meeting(request):
    # supposed to get the trainee id and the advisor id associated to the training program and sends that to this
    # form view it also MUST call the function that handles meetings conflict
    token = request.cookies['token']
    advisor = token_helper.verify_token(token)
    if not advisor:
        flash("Invalid token", 'error')
        return redirect(url_for('auth.login_view'))
    registration_records = db.session.execute(text("""
        SELECT * from `training_registration` where `advisorID`= :advisorID
    """), {"advisorID": advisor["advisorID"]}).fetchall()
    if not registration_records:
        flash('Something went wrong')
        return redirect(request.referrer)
    else:
        return render_template('advisor/advisor-new-meeting.html', advisor=advisor,
                               registration_records=registration_records)


"""
    This is the function that handles the meeting addition request
"""


def handle_meeting_add(request):
    # get the trainee from token
    token = request.cookies['token']
    if not token:
        flash('Token not found, invalid request', 'error')
        return redirect(url_for('auth.login_view'))
    advisor = token_helper.verify_token(token)
    if not advisor:
        flash("Invalid whatever", 'error')
        return redirect(request.referrer)
    # get meeting data from request
    registration_id = request.form['registrationID']
    meeting_details = request.form['details']
    start_datetime = request.form['start']
    end_datetime = request.form['end']
    params = {
        "registration_id": registration_id,
        "meeting_details": meeting_details,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime
    }
    if not meeting_details or not start_datetime or not end_datetime:
        flash("Missing data", 'error')
        return redirect(request.referrer)
    # check for conflict
    conflict = helper.resolve_conflict(new_meeting=params)
    # if no conflict then add the meeting pending for approval from advisor
    if conflict:
        flash("meetings conflict", 'error')
        return redirect(request.referrer)
    else:
        # insert meeting to the database
        params = {
            "registration_id": registration_id,
            "meeting_details": meeting_details,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime
        }
        result = db.session.execute(
            text(""" 
                INSERT INTO `meetings` (registration_id, meeting_details, start_datetime, end_datetime, status) 
                VALUES (:registration_id,:meeting_details, :start_datetime, :end_datetime, 'pending')
            """),
            params
        )
        if not result:
            flash("Failed to add meeting", 'error')
            return redirect(request.referrer)
        else:
            db.session.commit()
            flash("Waiting for advisor approval")
            return redirect(url_for('advisor.get_advisor_meetings_view'))


"""
    This is the function that handles account modifications requests. 
"""


def handle_profile_update(request):
    # the profile update request contains all the trainee information
    username = request.form['username']
    fullname = request.form['fullName']
    dicsipline = request.form['desiredField']
    email = request.form['email']
    # those value can not be null, there's a default value
    token = request.cookies['token']
    advisor = token_helper.verify_token(token)
    if not advisor:
        flash("Invalid token", 'error')
        return redirect(url_for('auth.login_view'))
    # proceed with the update
    query = text("""
            UPDATE `advisors` 
            SET `username`=:username,
            `fullname`=:fullname,
            `dicsipline`=:dicsipline,
            `email`=:email,
            `status` = 'in_review'
            WHERE `advisorID` = :advisorID;
        """)
    params = {
        "username": username,
        "fullname": fullname,
        "dicsipline": dicsipline,
        "email": email,
        "advisorID": advisor["advisorID"]
    }
    result_set = db.session.execute(query, params).rowcount
    # the user information is updated, but the thing is, this information must be reviewed, so the status must be
    # pending
    if result_set > 0:
        # success
        db.session.commit()
        flash('Account modification is in manager review, your account is onhold until. Check your email')
        return redirect(url_for('auth.login_view'))
    else:
        flash('Failed to submit account modification, try again', 'error')
        return redirect(url_for('advisorID.dashboard_view'))


"""
    This is the function that handles account deactivation requests.
"""


def handle_profile_deactivation(request):
    token = request.cookies['token']
    advisor = token_helper.verify_token(token)
    if not advisor:
        flash("Invalid token", 'error')
        return redirect(url_for('auth.login_view'))
    # proceed with the update
    query = text("""
                UPDATE `advisors` 
                SET `status` = 'inactive'
                WHERE `advisorID` = :advisorID;
            """)
    params = {
        "advisorID": advisor["advisorID"]
    }
    result_set = db.session.execute(query, params).rowcount
    # the user information is updated, but the thing is, this information must be reviewed, so the status must be pending
    if result_set > 0:
        # success
        db.session.commit()
        flash('Account deactivation is in manager review. Check your email')
        return redirect(url_for('auth.login_view'))
    else:
        flash('Failed to submit account deactivation, try again', 'error')
        return redirect(url_for('advisor.dashboard_view'))


def cancel_meeting(request, meetingID):
    # request has meetingID
    token = request.cookies['token']
    advisor = token_helper.verify_token(token)
    if not advisor:
        flash("Invalid token", 'error')
        return redirect(url_for('auth.login_view'))
    meeting_status = db.session.execute(
        text("select status from meetings where meetingID = :meetingID and status ='cancelled'"),
        {"meetingID": meetingID}).fetchone()
    if meeting_status:
        flash("already cancelled", 'error')
        return redirect(request.referrer)
    # update the status
    result = db.session.execute(
        text("""
        UPDATE `meetings`
        SET `status` = 'cancelled'
        where `meetingID` = :meetingID
        """),
        {"meetingID": meetingID}
    ).rowcount
    if not result:
        flash("Failed to cancel meeting")
        return redirect(request.referrer)
    else:
        db.session.commit()
        return redirect(url_for('advisor.get_advisor_meetings_view'))


def approve_meeting(request, meetingID):
    # request has meetingID
    token = request.cookies['token']
    advisor = token_helper.verify_token(token)
    if not advisor:
        flash("Invalid token", 'error')
        return redirect(url_for('auth.login_view'))
    meeting_record = db.session.execute(
        text("select * from meetings where meetingID = :meetingID"),
        {"meetingID": meetingID}).fetchone()
    if meeting_record[6] == 'approved':
        flash("already approved", 'error')
        return redirect(request.referrer)
    # check meeting conflict
    params={
        "registration_id": meeting_record[1],
        "start_datetime": meeting_record[4].strftime("%Y-%m-%dT%H:%M"),
        "end_datetime": meeting_record[5].strftime("%Y-%m-%dT%H:%M")

} 
    conflict = helper.resolve_conflict(new_meeting=params)
    if conflict:
        flash('failed to approve due to conflict', 'error')
        return redirect(request.referrer)
    # update the status
    result = db.session.execute(

        text("""
           UPDATE `meetings`
           SET `status` = 'approved'
           where `meetingID` = :meetingID
           """),
        {"meetingID": meetingID}
    ).rowcount
    if not result:
        flash("Failed to approve meeting")
        return redirect(request.referrer)
    else:
        db.session.commit()
        return redirect(url_for('advisor.get_advisor_meetings_view'))
