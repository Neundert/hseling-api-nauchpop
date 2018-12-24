from io import BytesIO
from os.path import join, getsize

from flask import Flask, jsonify, request, Response, send_file, make_response, redirect
from logging import getLogger


import boilerplate

from hseling_api_nauchpop.process import process_topic, process_rb



ALLOWED_EXTENSIONS = ['txt']

log = getLogger(__name__)


app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL=boilerplate.CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND=boilerplate.CELERY_RESULT_BACKEND
)
celery = boilerplate.make_celery(app)


@celery.task
def task_topic(file_ids_list=None):
    files_to_process = boilerplate.list_files(recursive=True,
                                              prefix=boilerplate.UPLOAD_PREFIX)
    if file_ids_list:
        files_to_process = [boilerplate.UPLOAD_PREFIX + file_id
                            for file_id in file_ids_list
                            if (boilerplate.UPLOAD_PREFIX + file_id)
                            in files_to_process]
    data_to_process = {file_id[len(boilerplate.UPLOAD_PREFIX):]:
                       boilerplate.get_file(file_id)
                       for file_id in files_to_process}
    processed_file_ids = list()
    for processed_file_id, contents in process_topic(data_to_process):
        processed_file_ids.append(
            boilerplate.add_processed_file(
                processed_file_id,
                contents,
                extension='txt'
            ))

    return processed_file_ids

@celery.task
def task_rb(file_ids_list=None):
    files_to_process = boilerplate.list_files(recursive=True,
                                              prefix=boilerplate.UPLOAD_PREFIX)
    if file_ids_list:
        files_to_process = [boilerplate.UPLOAD_PREFIX + file_id
                            for file_id in file_ids_list
                            if (boilerplate.UPLOAD_PREFIX + file_id)
                            in files_to_process]
    data_to_process = {file_id[len(boilerplate.UPLOAD_PREFIX):]:
                       boilerplate.get_file(file_id)
                       for file_id in files_to_process}
    processed_file_ids = list()
    for processed_file_id, contents in process_rb(data_to_process):
        processed_file_ids.append(
            boilerplate.add_processed_file(
                processed_file_id,
                contents,
                extension='txt'
            ))

    return processed_file_ids


@app.route('/upload', methods=['GET', 'POST'])
def upload_endpoint():
    if request.method == 'POST':

        if 'file' not in request.files:
            return jsonify({"error": boilerplate.ERROR_NO_FILE_PART})
        upload_file = request.files['file']
        #make upload for few files
        # uploaded_files = flask.request.files.getlist("file[]")
        if upload_file.filename == '':
            return jsonify({"error": boilerplate.ERROR_NO_SELECTED_FILE})
        if upload_file and boilerplate.allowed_file(
                upload_file.filename,
                allowed_extensions=ALLOWED_EXTENSIONS):
            return jsonify(boilerplate.save_file(upload_file))
    return boilerplate.get_upload_form()



@app.route('/files/<path:file_id>')
def get_file_endpoint(file_id):
    if file_id in boilerplate.list_files(recursive=True):
        return boilerplate.get_file(file_id)
    return jsonify({'error': boilerplate.ERROR_NO_SUCH_FILE})

@app.route('/files')
def list_files_endpoint():
    return jsonify({'file_ids': boilerplate.list_files(recursive=True)})


@app.route('/process', methods=['GET', 'POST'])
@app.route("/process/<file_ids>")
def process_endpoint(file_ids=None):
    if request.method == 'POST':
        process_types = request.data
        process_types = process_types.decode('utf-8')
        all_process_types = process_types.split(',')
        file_ids_list = file_ids and file_ids.split(",")
        task_list = []
        for process_type in all_process_types:
            if process_type == 'topic':
                task_1 = task_topic.delay(file_ids_list)
                task_dict_1 = {"task_1_id": str(task_1)}
                task_list.append(task_dict_1)
            elif process_type == 'rb':
                task_2 = task_rb.delay(file_ids_list)
                task_dict_2 = {"task_2_id": str(task_2)}
                task_list.append(task_dict_2)
            else:
                pass
        modules_to_process = {}
        if not task_list:
            return jsonify({'error': boilerplate.ERROR_NO_PROCESS_TYPE_SPECIFIED})
        else:
            for t in task_list:
                modules_to_process.update(t)
            return jsonify(modules_to_process)


@app.route("/status/<task_id>")
def status_endpoint(task_id):
    return jsonify(boilerplate.get_task_status(task_id))


def get_endpoints(ctx):
    def endpoint(name, description, active=True):
        return {
            "name": name,
            "description": description,
            "active": active
        }

    all_endpoints = [
        endpoint("root", boilerplate.ENDPOINT_ROOT),
        endpoint("scrap", boilerplate.ENDPOINT_SCRAP,
                 not ctx["restricted_mode"]),
        endpoint("upload", boilerplate.ENDPOINT_UPLOAD),
        endpoint("process", boilerplate.ENDPOINT_PROCESS),
        endpoint("status", boilerplate.ENDPOINT_STATUS)
    ]

    return {ep["name"]: ep for ep in all_endpoints if ep}


@app.route("/")
def main_endpoint():
    ctx = {"restricted_mode": boilerplate.RESTRICTED_MODE}
    return jsonify({"endpoints": get_endpoints(ctx)})


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=80)


__all__ = [app, celery]
