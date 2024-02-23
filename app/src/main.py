from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import *

main = Blueprint('main', __name__)

@main.route('/profile')
@login_required
def profile():
    return render_template(
        'user_profile.html', 
        name=current_user.name, 
        username=current_user.username,
        email=current_user.email,
        age=current_user.age,
        grade=current_user.grade.value,
        current_user=current_user, 
        logged_in=True
    )
    
@main.route('/lesson/<int:course_id>')
@login_required
def lesson_page(course_id):
    course = Course.query.get(course_id)

    # TODO: set up a conditional (like below in quiz_page) and an algorithm that parses 
    #       through course structure + lesson content and sends two dictionaries in a particular 
    #       format over to front-end, where it can be processed to generate an appropriate tab 
    #       structure and panel contents.

    modules = Module.query.filter_by(course_id=course_id).all()

    topics = {}
    for module in modules:
        topics[module.id] = Topic.query.filter_by(module_id=module.id).all()

    # Send in number of topics for a course to display on lessons page, easier to compute here than accessing dict values with Jinja2
    number_topics = sum(len(module_topics) for module_topics in topics.values())

    lessons = {}
    for module_topics in topics.values():
        for topic in module_topics:
            lessons[topic.id] = Lesson.query.filter_by(topic_id=topic.id).all()

    return render_template('lesson.html', current_user=current_user, logged_in=True, course=course, modules=modules, topics=topics, number_topics=number_topics, lessons=lessons)

@main.route('/quiz/<int:quiz_id>', methods=['GET'])
@login_required
def quiz_page(quiz_id):
    quiz = Quiz.query.get(quiz_id)

    # Temporary workaround since there are no quizzes right now, just to prevent an error
    if not quiz:
        questions = None
    else:
        questions = [(i + 1, question) for i, question in enumerate(quiz.questions)]

    return render_template('quiz.html', current_user=current_user, logged_in=True, quiz=quiz, questions=questions)

@main.route('/dashboard')
@login_required
def dashboard_page():
    user_progress = current_user.progress
    user_points = current_user.points
    return render_template('dashboard.html', current_user=current_user, logged_in=True, user_progress=user_progress)

@main.route('/test/dashboard')
def test_dashboard():
    return render_template('dashboard.html')

@main.route('/leaderboard')
@login_required
def leaderboard_page():
    leaderboard_data = Points.get_leaderboard()
    user_ranking = None
    
    user_points = Points.query.filter_by(user_id=current_user.id).first()
    if user_points:
        user_ranking = Points.query.filter(Points.points > user_points.points).count() + 1

    
    
    
    return render_template(
        'leaderboard.html', 
        name=current_user.name, 
        username=current_user.username,
        leaderboard_data=leaderboard_data, 
        user_ranking=user_ranking,
        logged_in=True
    )