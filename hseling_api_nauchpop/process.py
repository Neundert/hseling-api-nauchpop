from .topic_module.topic_classification import get_topic

def process_data(data_to_process):
    """Split all files contents and then combine unique words into resulting file.
    """

    for _, contents in data_to_process.items():
        if isinstance(contents, bytes):
            text = contents.decode('utf-8')
        else:
            text = contents
        result = get_topic(text)

    if result:
        yield None, result
