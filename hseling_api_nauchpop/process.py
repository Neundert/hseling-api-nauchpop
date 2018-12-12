from .topic_module.topic_classification import get_topic

def process_data(data_to_process):
    """make topic modeling for text
    """

    for _, contents in data_to_process.items():
        if isinstance(contents, bytes):
            text = contents.decode('utf-8')
        else:
            text = contents
        result = get_topic(text)
        print(result)
        print(type(result))
    if result:
        yield None, result
