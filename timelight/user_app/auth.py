from .lib.db_helper import *  
from flask import Blueprint, redirect, render_template, request, session, url_for, current_app, jsonify


auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@auth.route('/register', methods=['POST',])
def register():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    current_app.logger.info("Registering user")
    register_user(username, password, email)
    return serve_response(data="User registered successfully" , status_code=200)
    

@auth.route('/login', methods=['POST',])
def login():
    username = request.form['username']
    password = request.form['password']
    current_app.logger.info("Logging in user")
    user = login_user(username, password)
    return jsonify(user)
    

@auth.route('/logout', methods=['DELETE',])
def logout():
    userid = request.form['userid']
    session.clear() 
    return redirect(url_for('index'))


@auth.route('/delete', methods=['DELETE',])
def delete():
    username = request.form['username']
    current_app.logger.info('Deleting user')    
    delete_user(username) 
    return serve_response(data="User deleted", status_code=200)


@auth.route('/user', methods=['GET',])
def user():
    username = request.form['username']
    user = get_user(username)
    current_app.logger.info('Getting user')
    return jsonify(user)