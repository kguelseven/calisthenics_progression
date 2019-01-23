from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm
from app import app

@app.route("/")
@app.route("/index")
def index():
    # Mock User
    user = {'username' : 'Richi'}
    workouts = [
        {
            'athlet' : { 'username' : 'John'},
            'title' : 'Workout Day 1'
        },
        {
            'athlet' : { 'username' : 'Ali'},
            'title' : 'Workout Day 2'
        },

    ]
    return render_template('index.html', title='Home', user=user, workouts=workouts)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data))
        return redirect(url_for(index))
    return render_template('login.html', title='Sign In', form=form)