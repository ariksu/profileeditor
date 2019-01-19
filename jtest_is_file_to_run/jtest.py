import re
import json


def prepare_text_for_json(text: str) -> str:
    """
    remove extra commas, add { at the beginning anf } at the end of file, enclose keys in qoutes
    :param text: ini file text
    :return:  ini file text prepared for json converting
    """
    if r'"' in text:
        print(r'Not allowed symbol: "')
    text = text.strip()
    if text[0] != '{':
        text = '{' + text
        text = text + '}'
    # add qoutes
    text = re.sub(r'([A-Za-z0-9А-Яа-я]\w*)', r'"\1"', text)
    text = re.sub(r'"([0-9]+)"', r'\1', text)
    # remove tabulation
    text = text.replace("\t", "")
    # remove extra commas at },} and like this
    while re.findall(r",(\s*[\}\]])", text):
        text = re.sub(r",(\s*[\}\]])", r'\1', text)
    return text


# with open('prejson.ini') as f:
#     with open('correct.json','w') as o:
#             o.write(prepare_text_for_json(f.read()))

from quicktype import welcome_from_dict
with open('correct.json') as j:
    x = welcome_from_dict(json.load(j))
    from pprint import pprint

    # set breakpoint on pprint below to view loaded object in debugger
    pprint(x)


with open("incorrect.json") as j2:
    try:
        x2 = welcome_from_dict(json.load(j2))
    except Exception as e:
        print("failed to load incorrect json")
        print(e)
