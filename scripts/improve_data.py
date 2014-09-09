""" Rule-based training data enhancment """ 

import xml.etree.ElementTree as ET
import argparse
import unicodedata
import sys

from utils import to_unicode, print_out, tokenize, set_from_file, normalize, is_punct


COMMA_WORDS = [',', ';', '.', ':', '`', '\'', '-', '\',',
    'and', ', and', '; and']


INSTITUTION_DICT = 'dicts/institution_keywords.txt'
ADDRESS_DICT = 'dicts/my_address_keywords.txt'

def is_accent(char):
    return unicodedata.category(to_unicode(char)) in ['Sk', 'Lm']


def is_end_word_or_accent(text):
    text = text.strip()
    if not text:
        return True
    
    if is_accent(text[0]):
        text = text[1:].strip()
    if not text:
        return True
    
    if text in COMMA_WORDS:
        return True

    return False


def enhance_untagged(root):
    """ Glue hanging tails to texts if they are unimportant 
        (commas, hanging accents).
        Remove hanging tails if they are not followed by any tails.
        Otherwise drop affiliations. """
    
    for (i, aff) in enumerate(list(root)):
        if aff.text and aff.text.strip():
            root.remove(aff)
        else:
            for (j, elem) in enumerate(aff):

                elem.tail = elem.tail or ''
                elem.text = elem.text or ''

                if j == len(list(aff)) - 1: # Mostly rubbish like Submitted / Accepted
                    elem.tail = ''
                elif is_end_word_or_accent(elem.tail):
                    elem.text += elem.tail
                    elem.tail = ''
                elif len(elem.tail.strip()) <= 2:
                    """print "GLUEING %s + %s" % \
                            (to_unicode(elem.text).encode('utf8'),
                                    to_unicode(elem.tail).encode('utf8'))"""
                    elem.text += elem.tail
                    elem.tail = ''
                else:
                    #print "REMOVING"
                    #print_out(aff)
                    root.remove(aff)
                    break


def change_institution_by_order(root):
    """ <addr-line>A, </addr-line><institution>B</institution>... -->
        <institution>A, </institution><institution>B</institution>...
    """
    
    def short_rep(order):
        return ''.join(s[0].upper() for s in order)

    for aff in root:
        order = []
        last = None
        for elem in aff:
            tag = elem.tag
            if tag != last:
                last = tag
                order += [tag]
        rep = short_rep(order)

        if rep.startswith('AI'):
            for elem in aff:
                tag = elem.tag
                if tag == 'institution':
                    break
                if tag == 'addr-line':
                    #print_out(elem)
                    elem.tag = 'institution'


def split_by_commas(root):
    """ <tag> A, B </tag>.. -> <tag> A,</tag><tag> B </tag>... """
    
    def make_elem(tag, text):
        el = ET.Element(tag)
        el.text = text
        return el
    
    for aff in root:
        new_elems = []

        for elem in aff:
            current_text = ''
            tokens = tokenize(elem.text, keep_all=True)
            for t in tokens:
                current_text += t
                #if len(to_unicode(t)) == 1 and unicodedata.category(to_unicode(t)) == 'Po':
                if is_punct(t):
                    new_elems += [make_elem(elem.tag, current_text)]
                    current_text = ''
            if current_text:
                new_elems += [make_elem(elem.tag, current_text)]
            new_elems[len(new_elems) - 1].tail = elem.tail

        for elem in list(aff):
            aff.remove(elem)
        
        aff.extend(new_elems)


def change_institution_by_dict(root):
    """ <addr-line> InstitutionLikeWord <addr-line> --> 
        <institution> InstitutionLikeWord </institution>
    """

    split_by_commas(root)
    institution_keywords = set_from_file(INSTITUTION_DICT, normal=True)
    address_keywords = set_from_file(ADDRESS_DICT, normal=True)

    for aff in root:
        for elem in aff:
            if elem.tag == 'addr-line':
                tokens = [normalize(t) for t in tokenize(elem.text, split_alphanum=True)]
                if any(t in institution_keywords for t in tokens) \
                        and not any(t.isdigit() for t in tokens) \
                        and not any(t in address_keywords for t in tokens):
                    elem.tag = 'institution'
                    print_out(elem, sys.stderr)


def get_args():
    parser = argparse.ArgumentParser(description="Rule-based training data enhancment")
    
    parser.add_argument('--input', default='data/affs-matched.xml')
    parser.add_argument('--output', default='data/affs-improved.xml')
    
    return parser.parse_args()


if __name__ == '__main__':

    args = get_args()

    tree = ET.parse(args.input)
    root = tree.getroot()
    
    enhance_untagged(root)
    change_institution_by_dict(root)
    change_institution_by_order(root)
    
    tree.write(args.output)
