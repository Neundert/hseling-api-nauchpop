from .topic_module.topic_classification import get_topic
from .rb_module.count_all import count_all_metrics
def process_topic(data_to_process):
    """make topic modeling for text
    """

    for _, contents in data_to_process.items():
        if isinstance(contents, bytes):
            text = contents.decode('utf-8')
        else:
            text = contents
        result = get_topic(text)
    if result:
        yield None, result

def process_rb(data_to_process):
    for _, contents in data_to_process.items():
        if isinstance(contents, bytes):
            text = contents.decode('utf-8')
        else:
            text = contents
        result = count_all_metrics(text)

    if result:
        yield None, result





#this is mock function for testing
# def process_rb(data_to_process):
#     result = set()
#     for _, contents in data_to_process.items():
#         if isinstance(contents, bytes):
#             text = contents.decode('utf-8')
#         else:
#             text = contents
#         #result = count_all_metric(text)
#
#         result |= set(text.split())
#
#     if result:
#         yield None, '\n'.join(sorted(list(result)))
#     # if result:
#     #     yield None, ' '.join(result)
