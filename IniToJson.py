import re
import json
import sys
from typing import Tuple, Dict, Any, Optional


def remove_comments(text: str) -> Tuple[str, int]:
    """
    function removes commentns from ini file and returns new text and number of deleted lines
    :param text: text from ini file
    :return: text without comments, number of removed strings
    """
    missed = 0
    while "/*" in text:
        start = text.find("/*")
        end = text.find('*/')
        if end == -1:
            print('Comment started with /* is not closed')
        missed = text.count('\n', start, end)
        new_text = text[:start] + text[end + 2:]
        text = new_text
    lines = text.split('\n')
    text = ""
    for line in lines:
        if r'//' in line:
            new_line = line[:line.index(r'//')]
            text = text + new_line + '\n'
        else:
            text = text + line + '\n'
    return text, missed


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


def get_json(text: str) -> Tuple[Optional[Dict[Any, Any]], str]:
    """
    funtions converts prepared text to json if possible
    :param text: ini file text
    :return: json (as dictionary) (or None), empty string or error text
    """
    text, missed = remove_comments(text)
    text = prepare_text_for_json(text)
    try:
        data = json.loads(text)
        return data, ""
    except json.decoder.JSONDecodeError:
        e = sys.exc_info()
        if e is not None:
            err = e[1].msg
            line = e[1].lineno + missed
            # wrong error text in json lib
            if err == "Expecting ',' delimiter":
                err += ", ']' or '}'"
            err = "Line %i or %i: %s" % (line-1, line, err)
            return None, err
