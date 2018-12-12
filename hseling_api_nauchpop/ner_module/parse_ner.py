from bootstrap_ner import parse_user_text
from main import tomita
import re

# def detect_ner_tomita(user_text: str) -> None:
#
#     with open('./tomita-parser/build/bin/user_entry.txt', 'w') as fo:
#         fo.write(user_text)
#     shell = True)
#     subprocess.call("./tomita-parser/build/bin/tomita-parser ./tomita-parser/build/bin/config.proto",


def extract_ner(user_text: str) -> list:
    detect_ner_tomita(user_text)
    names = parse_user_text(user_text)
    return names

def markup_ner(user_text: str) -> None:
    def tag_names(user_text: str, names:list) -> str:
        search_pattern = '|'.join(names)
        replace_pattern = '<span class="name">\g<0></span>'
        return re.sub(search_pattern, replace_pattern, user_text)

    names = extract_ner(user_text)
    return tag_names(user_text, names)