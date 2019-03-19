from flask import Flask, jsonify, request, Response

import boilerplate

from hseling_api_nauchpop.process import process_topic,\
    process_rb, process_term, process_ner

ALLOWED_EXTENSIONS = ['txt']

# log = getLogger(__name__)

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL=boilerplate.CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND=boilerplate.CELERY_RESULT_BACKEND
)
celery = boilerplate.make_celery(app)


@celery.task
def task_topic(file_ids_list=None):
    data_to_process = boilerplate.get_process_data(file_ids_list)
    processed_file_ids = list()
    for processed_file_id, contents in process_topic(data_to_process):
        processed_file_ids.append(
            boilerplate.add_processed_file(
                boilerplate.TOPIC_PREFIX,
                processed_file_id,
                contents,
                extension='txt'
            ))

    return processed_file_ids


@celery.task
def task_rb(file_ids_list=None):
    data_to_process = boilerplate.get_process_data(file_ids_list)
    processed_file_ids = list()
    for processed_file_id, contents in process_rb(data_to_process):
        processed_file_ids.append(
            boilerplate.add_processed_file(
                boilerplate.RB_PREFIX,
                processed_file_id,
                contents,
                extension='txt'
            ))

    return processed_file_ids


@celery.task
def task_term(file_ids_list=None):
    data_to_process = boilerplate.get_process_data(file_ids_list)
    processed_file_ids = list()
    for processed_file_id, contents in process_term(data_to_process):
        processed_file_ids.append(
            boilerplate.add_processed_file(
                boilerplate.TERM_PREFIX,
                processed_file_id,
                contents,
                extension='txt'
            ))

    return processed_file_ids


@celery.task
def task_ner(file_ids_list=None):
    data_to_process = boilerplate.get_process_data(file_ids_list)
    processed_file_ids = list()
    for processed_file_id, contents in process_ner(data_to_process):
        processed_file_ids.append(
            boilerplate.add_processed_file(
                boilerplate.NER_PREFIX,
                processed_file_id,
                contents,
                extension='txt'
            ))

    return processed_file_ids


@app.route('/upload', methods=['GET', 'POST'])
def upload_endpoint():
    if request.method == 'POST':
        uploaded_files = request.files.getlist("file[]")
        # upload_file = request.files['file']
        # make upload for few files
        result_upload_file = {}
        for num, upload_file in enumerate(uploaded_files):
            if uploaded_files[num].filename == '':
                return jsonify({"error": boilerplate.ERROR_NO_SELECTED_FILE})
            if uploaded_files[num] and boilerplate.allowed_file(
                    uploaded_files[num].filename,
                    allowed_extensions=ALLOWED_EXTENSIONS):
                result_done = boilerplate.save_file(uploaded_files[num])
                result = {str(num): result_done}
                result_upload_file.update(result)
        return jsonify(result_upload_file)
    return boilerplate.get_upload_form()


@app.route('/files/<path:file_id>')
def get_file_endpoint(file_id):
    if file_id in boilerplate.list_files(recursive=True):
        contents = boilerplate.get_file(file_id)
        return Response(contents, mimetype='text/plain')
    return jsonify({'error': boilerplate.ERROR_NO_SUCH_FILE})


@app.route('/files')
def list_files_endpoint():
    return jsonify({'file_ids': boilerplate.list_files(recursive=True)})


@app.route('/process')
@app.route("/process/<file_ids>", methods=['GET', 'POST'])
def process_endpoint(file_ids=None):
    if request.method == 'POST':
        process_types = request.data
        process_types = process_types.decode('utf-8')
        all_process_types = process_types.split(',')
        print(file_ids, 'file_ids')
        file_ids_list = file_ids and file_ids.split(",")
        print(file_ids_list, "file_ids_list")
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
            elif process_type == 'term':
                task_3 = task_term.delay(file_ids_list)
                task_dict_3 = {"task_3_id": str(task_3)}
                task_list.append(task_dict_3)
            elif process_type == 'ner':
                task_4 = task_ner.delay(file_ids_list)
                task_dict_4 = {"task_4_id": str(task_4)}
                task_list.append(task_dict_4)
            else:
                pass
        modules_to_process = {}
        if not task_list:
            return jsonify(
                {'error': boilerplate.ERROR_NO_PROCESS_TYPE_SPECIFIED})
        elif not file_ids_list:
            return jsonify(
                {'error': boilerplate.ERROR_NO_SUCH_FILE})
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
