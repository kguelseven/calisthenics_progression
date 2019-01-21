from flask import render_template
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

