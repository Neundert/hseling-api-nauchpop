from .topic_module.topic_classification import get_topic
from .rb_module.count_all import count_all_metrics
from .term_extraction.term_extractor import get_terms
from .ner_module.ner_parser import extract_ner


def process_topic(data_to_process):
    """make topic modeling for text and readability metrics
    """
    result = ""
    for _, contents in data_to_process.items():
        if isinstance(contents, bytes):
            text = contents.decode('utf-8')
        else:
            text = contents
        result = get_topic(text)
    if result:
        yield None, result


def process_rb(data_to_process):
    result = ""
    for _, contents in data_to_process.items():
        if isinstance(contents, bytes):
            text = contents.decode('utf-8')
        else:
            text = contents
        result = count_all_metrics(text)
    if result:
        yield None, result


def process_term(data_to_process):
    result = ""
    for _, contents in data_to_process.items():
        if isinstance(contents, bytes):
            text = contents.decode('utf-8')
        else:
            text = contents
        result = get_terms(text)
    if result:
        yield None, result


def process_ner(data_to_process):
    result = ""
    for _, contents in data_to_process.items():
        if isinstance(contents, bytes):
            text = contents.decode('utf-8')
        else:
            text = contents
        result = extract_ner(text)
    if result:
        yield None, result
