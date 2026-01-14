from .lib.db_helper import *  
from flask import Blueprint, redirect, render_template, request, session, url_for, current_app, jsonify, send_file

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@auth.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return render_template("register.html")
        try:
            current_app.logger.info("Registering user")
            register_user(username, password)
        except Exception as e:
            current_app.logger.error(f"Error registering user: {e}")
            return render_template("register.html")
        return redirect(url_for("auth.login", username=username))
    return render_template("register.html")


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        return render_template("login.html")
    try:
        current_app.logger.info("Logging in user")
        user = login_user(username, password)
        if not user:
            return redirect(url_for("auth.login"))
        return redirect(url_for("auth.closet", username=user[1], userid=user[0]))
    except Exception as e:
        current_app.logger.error(f"Login error: {e}")
        return render_template("login.html")


@auth.route('/logout', methods=['POST'])
def logout():
    try:
        session.clear()
        return redirect(url_for('auth.index'))
    except Exception as e:
        current_app.logger.error(f"Logout error: {e}")
        return redirect(url_for("auth.index"))


@auth.route('/delete', methods=['POST'])
def delete():
    username = request.form.get('username')
    if not username:
        return jsonify({"error": "Username required"}), 400
    try:
        current_app.logger.info('Deleting user')    
        delete_user(username)
        return serve_response(data="User deleted", status_code=200)
    except Exception as e:
        current_app.logger.error(f"Delete error: {e}")
        return jsonify({"error": "Failed to delete user"}), 500


@auth.route('/closet', methods=['GET'])
def closet():
    userid = request.args.get("userid")
    username = request.args.get("username")
    print(username, userid)
    if not userid or not username:
        return redirect(url_for("auth.login"))
    try:
        current_app.logger.info('Getting user closet') 
        image_s3_uris = get_user_apparels(userid)
        images = [uri[0] for uri in image_s3_uris]
        return render_template("closet.html", closet=images, userid=userid, username=username)
    except Exception as e:
        current_app.logger.error(f"Closet retrieval error: {e}")
        return redirect(url_for("auth.index"))