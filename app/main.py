from io import BytesIO
from os.path import join, getsize

from flask import Flask, jsonify, request, Response
from logging import getLogger

import inotify.adapters

import boilerplate

from hseling_api_nauchpop.process import process_data
from hseling_api_nauchpop.query import query_data


ALLOWED_EXTENSIONS = ['txt']
TOMITA_PATH_IN = '/tomita/in'
TOMITA_PATH_OUT = '/tomita/out'

log = getLogger(__name__)


app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL=boilerplate.CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND=boilerplate.CELERY_RESULT_BACKEND
)
celery = boilerplate.make_celery(app)


@celery.task
def process_task(file_ids_list=None):
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
    for filename, file_contents in data_to_process.items():
        with open(join(TOMITA_PATH_IN, filename), 'wb') as f:
            f.write(file_contents)

    i = inotify.adapters.Inotify()

    i.add_watch(TOMITA_PATH_OUT)

    processed_file_ids = set()

    for (_, type_names, path, out_filename) in i.event_gen(yield_nones=False):
        print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format(
            path, out_filename, type_names))

        if not out_filename.startswith('.') and out_filename.endswith('.xml') and 'IN_CLOSE_WRITE' in type_names:
            full_filename = join(path, out_filename)
            with open(full_filename, 'rb') as f:
                contents = BytesIO(f.read())
                contents_length = getsize(full_filename)
                print(contents)
                generated_filename = boilerplate.add_processed_file(None, contents, "xml", contents_length)
                processed_file_ids.add(generated_filename)

        if len(processed_file_ids) >= len(set(data_to_process.keys())):
            break

    return list(processed_file_ids)


@app.route('/upload', methods=['GET', 'POST'])
def upload_endpoint():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"error": boilerplate.ERROR_NO_FILE_PART})
        upload_file = request.files['file']
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
        contents = boilerplate.get_file(file_id)
        if file_id.startswith(boilerplate.PROCESSED_PREFIX) and file_id.endswith('.xml'):
            return Response(contents, mimetype='text/xml')
        return Response(contents, mimetype='text/plain')
    return jsonify({'error': boilerplate.ERROR_NO_SUCH_FILE})


@app.route('/files')
def list_files_endpoint():
    return jsonify({'file_ids': boilerplate.list_files(recursive=True)})


@app.route('/process')
@app.route("/process/<file_ids>")
def process_endpoint(file_ids=None):
    file_ids_list = file_ids and file_ids.split(",")
    task = process_task.delay(file_ids_list)
    return jsonify({"task_id": str(task)})


@app.route("/query/<path:file_id>")
def query_endpoint(file_id):
    query_type = request.args.get('type')
    if not query_type:
        return jsonify({"error": boilerplate.ERROR_NO_QUERY_TYPE_SPECIFIED})
    processed_file_id = boilerplate.PROCESSED_PREFIX + file_id
    if processed_file_id in boilerplate.list_files(recursive=True):
        return jsonify({"result": query_data({
            processed_file_id: boilerplate.get_file(processed_file_id)
        }, query_type=query_type)})
    return jsonify({"error": boilerplate.ERROR_NO_SUCH_FILE})


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
        endpoint("query", boilerplate.ENDPOINT_QUERY),
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
