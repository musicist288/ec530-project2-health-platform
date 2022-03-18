from pathlib import Path
from flask import (
    Blueprint,
    request,
    current_app,
    jsonify
)
from ..speech2text import tasks
from .common import error_response
from werkzeug.utils import secure_filename

S2T_BLUEPRINT_API = Blueprint("speech2text", __name__)

@S2T_BLUEPRINT_API.route("", methods=["POST"])
def submitjob():
    errors = []
    if 'UPLOAD_FOLDER' not in current_app.config:
        errors.append("Application does not support file uploads")
        return error_response(errors=errors, status_code=501)

    file_ = request.files.get('file', None)
    filename = file_.filename if file_ else None
    if not filename:
        errors.append("No file was uploaded.")
        return error_response(errors=errors)

    if not Path(filename):
        errors.append("There was an error uploading the file.")
        return error_response(errors=errors, status_code=500)

    filename = secure_filename(filename)
    filepath = Path(current_app.config['UPLOAD_FOLDER']) / filename
    file_.save(filepath)
    result = tasks.process.delay(str(filepath.absolute().resolve()))
    return jsonify(task_id=result.id)


@S2T_BLUEPRINT_API.route("/<task_id>", methods=["GET"])
def get_result(task_id):
    result = None
    if not tasks.is_task_ready(task_id):
        status = "PENDING"
    else:
        status = "FINISHED"
        result = tasks.get_task_result(task_id)

    return jsonify(task_id=task_id, result=result, status=status)
