#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import unicodedata
import re
import codecs


def set_from_file(filename, normal=False):
    with codecs.open(filename, 'rb', encoding='utf8') as f:
        if normal:
            return set([normalize(l.rstrip()) for l in f])
        else:
            return set([l.rstrip() for l in f])

def glue_lists(lol):
    """ [[a, b], [c, d], [e]] -> [a, b, c, d, e] """
    return [item for sublist in lol for item in sublist]


def split_more(format_str, split_list, flags=0):
    """ split_more('\s+', ['ba ba', 'ke bab']) = ['ba', 'ba', 'ke', 'bab'] """
    pres = [re.split(format_str, string, flags=flags) for string in split_list]
    return glue_lists(pres)


def tokenize(text, keep_all=False, split_alphanum=False):
    text = text or ''
    space_splitter = '(\s+)' if keep_all else '\s+'
    split_list = [text]

    # 'kot pies' -> 'kot', 'pies' or 'kot', ' ', 'pies' (when keep_all = True)
    split_list = split_more(space_splitter, split_list)
    
    # 'kot_pies;lis9' -> 'kot', '_', 'pies', ';', 'lis9'
    split_list = split_more('(\W|_)', split_list, flags=re.U)
    
    if split_alphanum:
        # 'lis9' -> 'lis', '9'
        split_list = split_more('(\d+)', split_list)

    return filter(lambda x: x != '', split_list) # don't keep ''s


def to_unicode(string):
    return string if isinstance(string, unicode) else string.decode('utf8')


def normalize(string):
    """u'Aあä' -> 'aa'"""
    string = to_unicode(string)
    return unicodedata.normalize('NFKD', string).encode('ascii', 'ignore').lower()


def print_out(node):
    string = ET.tostring(node, encoding="utf-8")
    print string
