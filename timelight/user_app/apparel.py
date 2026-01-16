from .lib.db_helper import * 
from flask import Blueprint, request, current_app, send_file, jsonify


apparel = Blueprint("apparel", __name__, url_prefix="/closet")


@apparel.route('/apparel', methods=['GET',])
def get_apparel_image():
    image_uri = request.form['uri']  
    current_app.logger.info("Getting apparel")
    apparel_image = get_apparel(image_uri)
    return send_file(apparel_image, mimetype='image/png')


@apparel.route('/apparel', methods=['POST',])
def add_apparel():
    userid = request.form['userid']
    image_file = request.files['image']
    post_apparel(userid, image_file)           
    return serve_response(data="Apparel added", status_code=201)


@apparel.route('/closet', methods=['GET',])
def get_user_closet():
    userid = request.form['userid']
    current_app.logger.info("Getting closet apparels")
    apparel_ids = get_user_apparels(userid)
    data = jsonify({"apparels" : apparel_ids})
    return data


@apparel.route('/apparel', methods=['DELETE',])
def remove_apparel():
    userid = request.form['userid']
    uri = request.form['uri']
    response = delete_apparel(userid, uri)
    return serve_response(data="Deleted apparel", status_code=203)


@apparel.route('/closet', methods=['DELETE',])
def remove_closet():
    userid = request.form['userid']
    response = delete_closet(userid)
    return serve_response(data="Closet deleted", status_code=203)