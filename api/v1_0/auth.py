from flask import *
from werkzeug.security import generate_password_hash, check_password_hash
from db import dbsql as db
from api.v1_0.models import User
from flask_login import login_user, login_required, logout_user
from api.v1_0.email import validate
auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return  render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page
    if not user.email_confirm:
        flash('Please check Inbox to confirm your Email address')
        validate(email)
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page
    if user.is_guest():
        flash('Please sign up')
        return redirect(url_for('auth.signup')) # if the user doesn't exist or password is wrong, reload the page
    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect('/profile')

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        if user.is_guest():
            user = User.query.filter_by(email=email).first()
            user.password = generate_password_hash(password, method='sha256')
            user.name = name
            user.access = 1
            db.session.commit()
            if user.email_confirm:
                validate(email)
                flash('Please check your Inbox')
            return redirect(url_for('auth.signup'))
    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))
    if email == 'hildebrandt.julian@googlemail.com':
        new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), email_confirm = False, access = 3)
    else:
        new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), email_confirm = False, access = 1)
    db.session.add(new_user)
    db.session.commit()
    validate(email)
    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    flash('You need to confirm your Email in order to Sign up. Please check your Inbox')
    return redirect(url_for('auth.signup'))
    


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('weblogic.index'))