""" Used for matching raw string with corresponding tagged text from PubMed """


import xml.etree.ElementTree as ET
import ast
import codecs
import argparse

from collections import defaultdict
from utils import tokenize, normalize, to_unicode


NUM_LEN = len('2740170 ') # Assume all ids look like this


def xml_escape(c):
    """ Escapes '&'s """
    return u'&amp;' if c == u'&' else c


def write_xml(matching, f):
    """ `matching` contains a list of pairs (tagged_string, its_superstring)
        Tagged superstrings are written to the file `f'
    """
    for (tagged, raw) in matching:
        print >>f, '<aff>'
        #print tagged, raw
        i = 0
        tag_to_write = None
        for c in tagged:
            if len(c) > 1 and c[1] == '/': # closing tag
                f.write(c)
            elif len(c) > 1: # opening tag
                if tag_to_write:
                    f.write(tag_to_write)
                    tag_to_write = None
                tag_to_write = c
            else:
                while normalize(raw[i]) != normalize(c):
                    f.write(xml_escape(raw[i]))
                    i += 1

                if tag_to_write:
                    f.write(tag_to_write)
                    tag_to_write = None
                f.write(xml_escape(raw[i]))
                i += 1
            
        f.write(''.join(xml_escape(c) for c in raw[i:]))

        print >>f
        print >>f, '</aff>'


def is_subseq(s1, s2):
    """ Tests if s1 is a subseq of s2 """
    s1 = [normalize(c) for c in s1 if len(c) == 1] # ignore tags
    s2 = [normalize(c) for c in s2]

    i = 0
    for c in s1:
        if i == len(s2):
            return False
        while s2[i] != c:
            i += 1
            if i == len(s2):
                return False
        i += 1
    return True


def get_matching(tagged, raw):
    """ Returns a list of pairs (tagged_text, raw_text) where
        raw_text is a string from the list `raw` and
        tagged_text is the only string from the list `tagged`
        being a subsequence of raw_text.
    """
    matches = [(filter(lambda x: is_subseq(x, y), tagged), y) for y in raw]
    matching = [(li[0], y) for (li, y) in matches if len(li) == 1]
    return matching


def tag_string(el, opening=True):
    return '<' + ('' if opening else '/') + el.tag + '>'


def chars_from_aff(aff):
    """chars_from_aff('<aff>My <country>UK</country></aff>') = 
       'M', 'y', '<country>', 'U', 'K', '</country>'
    """
    def list_of_chars(string): # may be None
        return [c for c in string if c != ' '] if string else []


    chars = []
    chars += list_of_chars(aff.text)
    for element in aff:
        chars += [tag_string(element, opening=True)]
        chars += list_of_chars(element.text)
        chars += [tag_string(element, opening=False)]
        chars += list_of_chars(element.tail)
    return [to_unicode(c) for c in chars]


def get_dicts(root, text_file):
    """Returns a pair (tag_dict, str_dict). The keys correspond do document
       ids. tag_dict and str_dict contain lists of chars to be matched.
       Additionaly, the lists in tag_dict contain opening and closing tags"""

    tag_dict = defaultdict(list)
    for aff in root:
        num = int(aff.get('num'))
        tag_dict[num] += [chars_from_aff(aff)]

    str_dict = defaultdict(list)
    for line in text_file:
        num = int(line.split()[0])
        str_dict[num] += [list(to_unicode(line[NUM_LEN:].rstrip()))]

    return tag_dict, str_dict


def match_text(root, text_file, doc_num, out_file):
    """Creates tags in the `text_file` using the content of the XML
       tree in `root`, writest the improved text to the `out_file`.
       Percentage and number of the lines tagged is printed to stdout.
       If `doc_num` != 0 only the affiliations from the one document are
       processed.
    """
    tag_dict, str_dict = get_dicts(root, text_file)
    
    total = 0
    matched = 0
        
    print >>out_file, tag_string(root, opening=True)

    docs_to_process = [doc_num] if doc_num != 0 else tag_dict.keys()

    for doc in docs_to_process:
        matching = get_matching(tag_dict[doc], str_dict[doc])
        matched += len(matching)
        total += len(str_dict[doc])
        write_xml(matching, out_file)

    print >>out_file, tag_string(root, opening=False)

    print 'amount of matched strings: %f, matched: %d, total %d' \
            % (matched / float(total), matched, total)


def get_args():
    parser = argparse.ArgumentParser(description="Tags the strings in the `raw` "
            "file according to the `xml` file and writes the new XML to the "
            "`out` file. If `doc` is specified, only one document is processed.")
    
    parser.add_argument('--xml', default='data/affs-stripped.xml')
    parser.add_argument('--raw', default='data/affs-string.txt')
    parser.add_argument('--out', default='data/affs-matched.xml')
    parser.add_argument('--doc', type=int, default=0)
    
    return parser.parse_args()


if __name__ == '__main__':

    args = get_args()

    text_file = codecs.open(args.raw, 'rb', encoding='utf8')
    out_file = codecs.open(args.out, 'wb', encoding='utf8')

    tree = ET.parse(args.xml)
    root = tree.getroot()
    
    match_text(root, text_file, args.doc, out_file)

