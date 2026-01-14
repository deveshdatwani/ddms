from .lib.db_helper import *
from flask import Blueprint, request, current_app, send_file, jsonify, redirect, url_for

apparel = Blueprint("apparel", __name__, url_prefix="/closet")


@apparel.route('/post/apparel', methods=['POST'])
def add_apparel():
    try:
        userid = request.form.get('userid')
        username = request.form.get('username')
        image_file = request.files.get('image')
        if not userid or not image_file:
            current_app.logger.warning("Missing userid or image in add_apparel")
            return redirect(url_for("auth.closet", userid=userid, username=username))
        image_file = correct_image_orientation(image_file)
        success = post_apparel(userid, image_file)
        if not success:
            current_app.logger.error("Failed to post apparel")
            return jsonify({"error": "Failed to add apparel"}), 500
        return redirect(url_for("auth.closet", userid=userid, username=username))
    except Exception as e:
        current_app.logger.error(f"Exception in add_apparel: {e}")
        return jsonify({"error": "Internal server error"}), 500


@apparel.route('/apparel', methods=['DELETE'])
def remove_apparel():
    try:
        uri = request.form.get('uri')
        if not uri:
            current_app.logger.warning("Missing uri in remove_apparel")
            return jsonify({"error": "uri required"}), 400
        success = delete_apparel(uri)
        if not success:
            current_app.logger.error(f"Failed to delete apparel {uri}")
            return jsonify({"error": "Failed to delete apparel"}), 500
        current_app.logger.info(f"Deleted apparel {uri}")
        return '', 203
    except Exception as e:
        current_app.logger.error(f"Exception in remove_apparel: {e}")
        return jsonify({"error": "Internal server error"}), 500


@apparel.route('/image_proxy', methods=['GET', 'POST'])
def image_proxy():
    try:
        uri = request.args.get('uri')
        if not uri:
            current_app.logger.warning("Missing uri parameter in image_proxy")
            return jsonify({"error": "uri parameter is required"}), 400
        img_file = get_apparel(uri)  # get_apparel returns BytesIO or None
        if not img_file:
            current_app.logger.warning(f"Image not found for uri: {uri}")
            return jsonify({"error": "Image not found"}), 404
        img_file.seek(0)
        return send_file(img_file, mimetype='image/png')
    except Exception as e:
        current_app.logger.error(f"Exception in image_proxy: {e}")
        return jsonify({"error": "Internal server error"}), 500