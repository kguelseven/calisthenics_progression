from flask import render_template
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

@app.route("/login")
def login():
    form = LoginForm()
    return render_template('login.html', title='Sign In', form=form)