#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import unicodedata
import re
import sys
import codecs


def xml_escape(s):
    """ Escapes '&'s """
    return re.sub('&', '&amp;', s)


def is_punct(char):
    return char in [',', ';', '.']


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
    
    forbidden = [''] if keep_all else ['', ' ']

    return filter(lambda x: normalize(x) not in forbidden, split_list) # don't keep ''s


def to_unicode(string):
    return string if isinstance(string, unicode) else string.decode('utf8')


def remove_em_dashes(string):
    return string.replace(unicodedata.lookup('EM DASH'), '-')


def normalize(string, lowercase=True):
    """u'Aあä' -> 'aa' or -> 'Aa' (depending on the flag lowercase)"""
    string = to_unicode(string)
    string = remove_em_dashes(string)
    normalized = unicodedata.normalize('NFKD', string).encode('ascii', 'ignore')
    if lowercase:
        return normalized.lower()
    else:
        return normalized


def print_out(node, where=sys.stdout):
    string = ET.tostring(node, encoding="utf-8")
    print >>where, string


def text_in_element(elem):
    return ''.join(txt for txt in elem.itertext())


def create_xml_tree(filename):
    with codecs.open(filename, 'rb', encoding='utf8') as input_file:
        root = ET.Element('affs')
        for line in input_file:
            aff = ET.SubElement(root, 'aff')
            aff.text = line
        return ET.ElementTree(root)
