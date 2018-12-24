# import readability_old as readtrad
from .readability_old import stringer, rb_stringer
from .pos_tags import pos_stringer
from .readability_dictionary_compare import dict_stringer

def count_all_metrics(text):
    all_metr = [stringer(text), rb_stringer(text),
                pos_stringer(text), dict_stringer(text)]
    final = ' '.join(all_metr)
    return final