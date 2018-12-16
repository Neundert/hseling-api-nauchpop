from io import BytesIO
from os.path import join, getsize

from flask import Flask, jsonify, request, Response, send_file, make_response, redirect, send_from_directory,send_file
from logging import getLogger


import boilerplate

from hseling_api_nauchpop.process import process_topic, process_rb  # NOQA
# from hseling_api_nauchpop.query import query_data


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
        # uploaded_files = flask.request.files.getlist("file[]")
        # print(uploaded_files)
        if upload_file.filename == '':
            return jsonify({"error": boilerplate.ERROR_NO_SELECTED_FILE})
        if upload_file and boilerplate.allowed_file(
                upload_file.filename,
                allowed_extensions=ALLOWED_EXTENSIONS):
            return jsonify(boilerplate.save_file(upload_file))
    # return ''
    return boilerplate.get_upload_form()



@app.route('/files/<path:file_id>')
def get_file_endpoint(file_id):
    # if file_id in boilerplate.list_files(recursive=True):
    #     return boilerplate.get_file(file_id)
    if file_id in boilerplate.list_files(recursive=True):
        response = make_response(boilerplate.get_file(file_id))
        response.headers["Content-Disposition"] = "" \
                                                  "attachment; filename=%s" % file_id
        return response
    # if file_id == "gold":
    #     query_type = request.args.get('type')
    #     processed_file, file_id = boilerplate.get_gold(query_type)
    #     return send_file(processed_file, mimetype='txt', attachment_filename=file_id, as_attachment=True)
    #

    return jsonify({'error': boilerplate.ERROR_NO_SUCH_FILE})

@app.route('/files')
def list_files_endpoint():
    return jsonify({'file_ids': boilerplate.list_files(recursive=True)})


@app.route('/process', methods=['GET', 'POST'])
@app.route("/process/<file_ids>")
def process_endpoint(file_ids=None):
    if request.method == 'POST':
        # API_ENDPOINT="http://0.0.0.0/process"
        #на вебе: modules="ner,topic,br"
        ## data to be sent to api
#          data = {'process_types':modules}
#          r = requests.post(url=API_ENDPOINT, data=data)
        process_types = request.data
        process_types = process_types.decode('utf-8')
        print(process_types)
        all_process_types = process_types.split(',')
        file_ids_list = file_ids and file_ids.split(",")
        for process_type in all_process_types:
            if process_type == 'topic':
                task_1 = task_topic.delay(file_ids_list)
            elif process_type == 'rb':
                task_2 = task_rb.delay(file_ids_list)

        return jsonify({"task_1_id": str(task_1), "task_2_id": str(task_2)})
            # continue
            # if process_type == 'rb':
            #     task = task_rb.delay(file_ids_list)
            #     print('good')
            #     filename = boilerplate.PROCESSED_PREFIX + str(task) + ".txt"
            # #     print('good')
            # #     return redirect('http://0.0.0.0/files/'+ boilerplate.PROCESSED_PREFIX + str(task) + ".txt")
            #     return jsonify({"task_id": str(task),"file_id": filename})



#    process_type = request.args.get('type')
#    if not process_type:
 #       return jsonify({"error": boilerplate.ERROR_NO_QUERY_TYPE_SPECIFIED})

    # file_ids_list = file_ids and file_ids.split(",")
    #
    # if
    # task = process_task.delay(file_ids_list)
    # return jsonify({"task_id": str(task)})



# @app.route("/query/<path:file_id>")
# def query_endpoint(file_id):
#     query_type = request.args.get('type')
#     if not query_type:
#         return jsonify({"error": boilerplate.ERROR_NO_QUERY_TYPE_SPECIFIED})
#     processed_file_id = boilerplate.PROCESSED_PREFIX + file_id
#     if processed_file_id in boilerplate.list_files(recursive=True):
#         return jsonify({"result": query_data({
#             processed_file_id: boilerplate.get_file(processed_file_id)
#         }, query_type=query_type)})
#     return jsonify({"error": boilerplate.ERROR_NO_SUCH_FILE})


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
        # endpoint("query", boilerplate.ENDPOINT_QUERY),
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
