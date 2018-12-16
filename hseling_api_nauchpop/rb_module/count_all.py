# import readability_old as readtrad
from .readability_old import stringer, rb_stringer
from .pos_tags import pos_stringer
from .readability_dictionary_compare import dict_stringer
# import pos_tags as pos_tags
# import readability_dictionary_compare as dict_metr

def count_all_metrics(text):
    all_metr = [stringer(text), rb_stringer(text),
                pos_stringer(text), dict_stringer(text)]
    final = ' '.join(all_metr)
    return final
    
