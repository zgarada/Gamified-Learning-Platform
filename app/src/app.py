from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .models import db, User, Points, Teacher
from .auth import auth as auth_blueprint
from .main import main as main_blueprint
from .routes import routes as routes_blueprint
from .lesson_api import api as api_blueprint
from .utils.quizSubmit import quiz_api as quiz_blueprint
from dotenv import load_dotenv
from sqlalchemy import desc
import os
from .seed_script import load_database

load_dotenv()

def create_app(test_config=None):

    app = Flask(__name__)

    # Configure and initialize database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['PER_PAGE'] = 10
    app.secret_key = os.getenv('SECRET_KEY')
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(routes_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(quiz_blueprint)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    if test_config:
        app.config.update(test_config)
    
    db.init_app(app)

    @app.route('/home')
    def home():
        if session.get('login_type') is None:
            session['login_type'] = None
            
        return render_template('home.html')

    @app.route('/')
    def index():          
        return redirect(url_for('home'))
    
    @login_manager.user_loader
    def load_user(user_id):
        # Check both User and Teacher tables for the user_id
        user = User.query.get(int(user_id))
        teacher = Teacher.query.get(int(user_id))
        # Return the user or teacher, depending on the login type from session
        if session["login_type"] == "teacher":
            return teacher
        elif session["login_type"] == "student":
            return user
        else:
            return None


    with app.app_context():
        db.create_all()
        load_database()

    return app