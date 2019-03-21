from .topic_module.topic_classification import get_topic
from .rb_module.count_all import count_all_metrics
from .term_extraction.term_extractor import get_terms
from .ner_module.ner_parser import extract_ner


def process(data, func):
    '''function to decode data if it's needed and
    process one of modules' functions'''

    result = list()
    for _, contents in data.items():
        if isinstance(contents, bytes):
            text = contents.decode('utf-8')
        else:
            text = contents
        result.append(str(_ + "\t" + func(text)))
    return result


def process_topic(data_to_process):

    result = process(data_to_process, get_topic)
    if result:
        yield None, '\n'.join(result)


def process_rb(data_to_process):

    result = process(data_to_process, count_all_metrics)
    if result:
        yield None, '\n'.join(result)


def process_term(data_to_process):

    result = process(data_to_process, get_terms)
    if result:
        yield None, '\n'.join(result)


def process_ner(data_to_process):

    result = process(data_to_process, extract_ner)
    if result:
        yield None, '\n'.join(result)
