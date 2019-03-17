from functools import wraps
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from project import db, app
from project.models import User, Workout, Exercises, Exercise, Set, Message, Notification
from project.main import bp
from project.main.forms import MessageForm
from project._config import WORKOUTS_PER_PAGE
from project.decorators import check_confirmed


# helper functions
@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# routes

@bp.route("/", methods=['GET', 'POST'] )
@bp.route("/index", methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.workouts'))
    return render_template('index.html', title='Home')

@bp.route("/workouts", methods=['GET', 'POST'])
@login_required
def workouts():
    page = request.args.get('page', 1, type=int)
    user = current_user.get_id()
    workouts = Workout.query.filter_by(user_id=current_user.get_id()).order_by(Workout.timestamp.desc()).paginate(page, app.config['WORKOUTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=workouts.next_num) if workouts.has_next else None
    prev_url = url_for('main.index', page=workouts.prev_num) if workouts.has_prev else None
    return render_template('workouts.html', title='Home', workouts=workouts.items, next_url=next_url, prev_url=prev_url)

@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    workouts = Workout.query.filter(Workout.user_id != current_user.id).order_by(Workout.timestamp.desc()).paginate(page, app.config['WORKOUTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=workouts.next_num) if workouts.has_next else None
    prev_url = url_for('main.explore', page=workouts.prev_num) if workouts.has_prev else None
    return render_template('explore.html', title='Explore', workouts=workouts.items, next_url=next_url, prev_url=prev_url)

@bp.route('/add_workout', methods=['POST', 'GET'])
@login_required
@check_confirmed
def add_workout():
    if request.method == 'POST':
        user = current_user

        workout = Workout(timestamp=datetime.utcnow(), user_id=user.id, title=request.form['wtitle'])

        exercise_count = int(request.form['exercise_count'])

        for exercise_num in range(1,exercise_count + 1):
            exercise = Exercise(exercise_order=exercise_num, exercise_id=request.form['exercise'+str(exercise_num)], workout=workout)

            progressions = request.form.getlist('progression' + str(exercise_num))
            reps = request.form.getlist('reps' + str(exercise_num))
            db.session.add(workout)
            exercise = Exercise.query.order_by(Exercise.id.desc()).first()
            set_order = 1
            for progression, rep in zip(progressions, reps):
                work_set = Set(set_order=set_order, exercise=exercise, progression=progression, reps=rep)
                set_order += 1

        db.session.add(work_set)
        db.session.commit()

        return redirect(url_for('main.index'))
    exercises = Exercises.query.all()
    return render_template('add_workout.html', exercises=exercises)

@bp.route('/user/<username>')
@login_required
@check_confirmed
def user(username):
    user = User.query.filter_by(username=username) .first_or_404()
    page = request.args.get('page', 1, type=int)
    workouts = user.workouts.order_by(Workout.timestamp.desc()).paginate(page, app.config['WORKOUTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=workouts.next_num) \
        if workouts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=workouts.prev_num) \
        if workouts.has_prev else None
    return render_template('user.html', user=user, workouts=workouts.items, next_url=next_url, prev_url=prev_url)

@bp.route('/follow/<username>')
@login_required
@check_confirmed
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('main.user', username=username))

@bp.route('/unfollow/<username>')
@login_required
@check_confirmed
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('main.user', username=username))

@bp.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(Message.timestamp.desc()).paginate(page, app.config['WORKOUTS_PER_PAGE'], False)
    next_url = url_for('main.messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('main.messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('messages.html', messages=messages.items, next_url=next_url, prev_url=prev_url)

@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(athlet=current_user, recipient=user, body=form.message.data)
        db.session.add(msg)
        user.add_notification('unread_message_count', user.new_messages())
        db.session.commit()
        flash('Your message has been sent.')
        return redirect(url_for('main.user', username=recipient))
    return render_template('send_message.html', title='Send Message', form=form, recipient=recipient)

@bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])