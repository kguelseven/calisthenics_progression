from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from project import db
from project.auth import bp
from project.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm, EditProfileForm
from project.auth.email import send_email
from project.models import User
from project.token import generate_confirmation_token, confirm_token
from project.decorators import check_confirmed


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
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
@check_confirmed
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('auth.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, confirmed=False, admin=False)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        token = generate_confirmation_token(user.email)
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)
        html = render_template('email/activate.html', confirm_url=confirm_url)
        subject = 'Please confirm your email'
        send_email(user.email, subject, html)

        login_user(user)
        flash('A confirmation email has been sent via email.', 'success')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/confirm/<token>')
@login_required
def confirm_email(token):
    if current_user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
        return redirect(url_for('main.index'))
    email = confirm_token(token)
    user = User.query.filter_by(email=current_user.email).first_or_404()
    if user.email == email:
        user.confirmed = True
        user.confirmed_on = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    else:
        flash('The confirmation link is invalid or has expired.', 'danger')
    return redirect(url_for('main.index'))

@bp.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@bp.route('/resend')
@login_required
def resend_confirmation():
    token = generate_confirmation_token(current_user.email)
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    html = render_template('email/activate.html', confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(current_user.email, subject, html)
    flash('A new confirmation email has been sent.', 'success')
    return redirect(url_for('auth.register'))

@bp.route('/forgot',  methods=['GET', 'POST'])
def forgot():
    form = ResetPasswordRequestForm(request.form)
    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()
        token = generate_confirmation_token(user.email)

        user.password_reset_token = token
        db.session.commit()

        reset_url = url_for('auth.forgot_new', token=token, _external=True)
        html = render_template('auth/reset.html',
                               username=user.email,
                               reset_url=reset_url)
        subject = "Reset your password"
        send_email(user.email, subject, html)

        flash('A password reset email has been sent via email.', 'success')
        return redirect(url_for("main.index"))

    return render_template('auth/forgot.html', form=form)


@bp.route('/forgot/new/<token>', methods=['GET', 'POST'])
def forgot_new(token):

    email = confirm_token(token)
    user = User.query.filter_by(email=email).first_or_404()

    if user.password_reset_token is not None:
        form =  ResetPasswordForm(request.form)
        if form.validate_on_submit():
            user = User.query.filter_by(email=email).first()
            if user:
                user.set_password(form.password.data)
                user.password_reset_token = None
                db.session.commit()

                login_user(user)

                flash('Password successfully changed.', 'success')
                return redirect(url_for('auth.login'))

            else:
                flash('Password change was unsuccessful.', 'danger')
                return redirect(url_for('auth.login'))
        else:
            flash('You can now change your password.', 'success')
            return render_template('auth/forgot_new.html', form=form)
    else:
        flash('Can not reset the password, try again.', 'danger')

    return redirect(url_for('main.index'))

'''
@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
'''


