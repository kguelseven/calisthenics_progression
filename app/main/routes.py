from functools import wraps
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from app import db, app
from app.main.forms import EditProfileForm, WorkoutForm
from app.models import User, Workout, Exercises, Exercise, Set
from app.main import bp
from app._config import WORKOUTS_PER_PAGE

# helper functions
@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# routes

@bp.route('/add_workout', methods=['POST', 'GET'])
def add_workout():
    if request.method == 'POST':
        user = User.query.filter_by(username=User.username).first()

        workout = Workout(timestamp=datetime.utcnow(), user_id=user.id, title=user.username)

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

@bp.route("/", methods=['GET', 'POST'] )
@bp.route("/index", methods=['GET', 'POST'])
@login_required
def index():
    form = WorkoutForm()
    if form.validate_on_submit():
        workout = Workout(title=form.workout.data, athlet=current_user)
        db.session.add(workout)
        db.session.commit()
        flash('Your workout is now live!')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    workouts = current_user.followed_workouts().paginate(page, app.config['WORKOUTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=workouts.next_num) \
        if workouts.has_next else None
    prev_url = url_for('main.index', page=workouts.prev_num) \
        if workouts.has_prev else None
    return render_template('index.html', title='Home', form=form, workouts=workouts.items, next_url=next_url, prev_url=prev_url)

@bp.route('/history/')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    workouts = Workout.query.order_by(Workout.timestamp.desc()).paginate(page, app.config['WORKOUTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=workouts.next_num) \
        if workouts.has_next else None
    prev_url = url_for('main.explore', page=workouts.prev_num) \
        if workouts.has_prev else None
    return render_template('history.html', title='History', workouts=workouts.items, next_url=next_url, prev_url=prev_url)
    
@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    workouts = Workout.query.order_by(Workout.timestamp.desc()).paginate(page, app.config['WORKOUTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=workouts.next_num) \
        if workouts.has_next else None
    prev_url = url_for('main.explore', page=workouts.prev_num) \
        if workouts.has_prev else None
    return render_template('index.html', title='Explore', workouts=workouts.items, next_url=next_url, prev_url=prev_url)

@bp.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data) .first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username) .first_or_404()
    page = request.args.get('page', 1, type=int)
    workouts = user.workouts.order_by(Workout.timestamp.desc()).paginate(page, app.config['WORKOUTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=workouts.next_num) \
        if workouts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=workouts.prev_num) \
        if workouts.has_prev else None
    return render_template('user.html', user=user, workouts=workouts.items, next_url=next_url, prev_url=prev_url)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@bp.route('/follow/<username>')
@login_required
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