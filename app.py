import os
from flask import Flask, render_template
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from helpers.logger import Logger

# Load env variables
load_dotenv('.env')

# Setup flask app instance
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://{0}:{1}@{2}/{3}".format(db_user, db_password, db_host, db_name)
app.config['USER_UPLOADS'] = '/static/user-uploads/'
db = SQLAlchemy(app)

# prepare logger
logger = Logger()  # Create a single instance of the Logger class

# Register app blueprints here
from blueprints.auth_blueprint import auth_blueprint

app.register_blueprint(auth_blueprint)
from blueprints.trainee_blueprint import trainee_blueprint

app.register_blueprint(trainee_blueprint)
from blueprints.manager_blueprint import manager_blueprint

app.register_blueprint(manager_blueprint)
from blueprints.advisor_blueprint import advisor_blueprint

app.register_blueprint(advisor_blueprint)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
 