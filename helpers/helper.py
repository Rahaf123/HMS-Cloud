 from app import db
from sqlalchemy import text
from datetime import datetime
import boto3
from app import logger

"""This is a private helper function, aims to check all meetings related to a trainee and an advisor The trainee and 
advisor can only request for meeting whenever there's a training between them. The function searches for conflicts by 
fetching all advisor meetings, all trainee meetings and check the conflict between each one and the other."""


def resolve_conflict(new_meeting):
    # get the registration record, which links between the advisor and trainee
    registration_record = db.session.execute(text("""
            SELECT * from `training_registration` where `ID` = :registration_id
    """), {
        "registration_id": int(new_meeting["registration_id"])
    }).fetchone()
    # just a validation I am used to do, I don't know why
    if not registration_record:
        return False
    # get all the trainee meetings
    traineeID = registration_record[2]  # traineeID field order in the database
    advisorID = registration_record[3]  # advisorID field order in the database
    # to get all the meetings related to an advisor or a trainee, you must join the training registration with the
    # meetings
    trainee_meetings = db.session.execute(text("""
                SELECT `meetingID`,`start_datetime`,`end_datetime`,meetings.`status`
                from (`meetings` JOIN `training_registration` on meetings.`registration_id` = training_registration.`ID`)
                WHERE training_registration.`status` = 'approved' 
                GROUP BY training_registration.`traineeID` 
                HAVING training_registration.`traineeID` = :traineeID;
    """), {
        "traineeID": traineeID
    }).fetchall()
    # get all the advisor meetings
    advisor_meetings = db.session.execute(text("""
            SELECT `meetingID`,`start_datetime`,`end_datetime`,meetings.`status`
            from (`meetings` JOIN `training_registration` on meetings.`registration_id` = training_registration.`ID`)
            WHERE training_registration.`status` = 'approved' 
            GROUP BY training_registration.`advisorID` 
            HAVING training_registration.`advisorID` = :advisorID;
    """), {
        "advisorID": advisorID
    }).fetchall()
    if trainee_meetings and advisor_meetings:
        conflicts = []
        for meeting in advisor_meetings + trainee_meetings:
            if meeting[1] < datetime.strptime(new_meeting["end_datetime"], "%Y-%m-%dT%H:%M") and datetime.strptime(
                    new_meeting["start_datetime"], "%Y-%m-%dT%H:%M") < meeting[2]:
                conflicts.append(meeting)
        if len(conflicts) == 0:
            # length of conflicts equal to zero, then no conflicts occured and you can add
            # TODO: Handle conflicts (e.g., reschedule conflicting meetings or notify the parties) -- or no need
            return False
        return True


"""
    This helper function uses AWS SES to send emails. 
"""


def send_email(recipient, message, subject, sender):
    ses_client = boto3.client('ses', region_name='eu-north-1')
    email_message = {
        'Subject': {'Data': subject},
        'Body': {'Text': {'Data': message}},
    }
    response = ses_client.send_email(
        Source=sender,
        Destination={'ToAddresses': [recipient]},
        Message=email_message)
    logger.log('One email is sent, details: To: {0}, From: {1}, Subject:{2}'.format(recipient, sender, subject))
    return response
