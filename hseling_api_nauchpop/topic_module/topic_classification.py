# Imports
import pickle
import re
import pymorphy2
from stop_words import get_stop_words


def load_model(filename):
    with open(filename, 'rb') as file:
        model = pickle.load(file)
    return model


vect_model = load_model('hseling_api_nauchpop/topic_module/models/model_vect.pkl')
reduce_model = load_model('hseling_api_nauchpop/topic_module/models/model_reduce.pkl')
classify_model = load_model('hseling_api_nauchpop/topic_module/models/model_class.pkl')


def preprocess(text):
    morph = pymorphy2.MorphAnalyzer()
    stopwords = get_stop_words('russian')
    words = re.findall(r'[a-zа-яё]+', text.lower())
    lemmas = [morph.parse(word)[0].normal_form for word in words if word not in stopwords]
    return [' '.join(lemmas)]


def vectorize(text, model):
    return model.transform(text)


def classify(text_vec, model):
    return model.predict(text_vec.reshape(1, -1))


def get_topic(text, vectorizer=vect_model, reducer=reduce_model, classifier=classify_model):
    lemm_text = preprocess(text)
    vect_text = vectorize(lemm_text, vectorizer)
    if reducer:
        vect_text = vectorize(vect_text, reducer)
    return classifier.predict(vect_text[0].reshape(1, -1))[0]
