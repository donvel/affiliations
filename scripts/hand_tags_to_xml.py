""" Export "fast tags" to tagged XML """

import argparse
import codecs
import re

from utils import xml_escape

def write_tagged(text, tag, xml_file):
    print >>xml_file, '<%s>%s</%s>' % (tag, xml_escape(text), tag)

def export_tags(text_file, xml_file, add_author):

    print >>xml_file, '<affs>'

    for line in text_file:
        line = line.rstrip();
        if not line:
            continue

        prefix = ''
        suffix = ''
        
        parts = re.split('<', line)
        if len(parts) > 1:
            assert len(parts) == 2
            line = parts[1]
            prefix = parts[0]
        
        parts = re.split('>', line)
        if len(parts) > 1:
            assert len(parts) == 2
            line = parts[0]
            suffix = parts[1]
        
        parts = re.split('\$', line)
        if len(parts) != 3:
            print parts
            continue

        print >>xml_file, '<aff>'
        if prefix:
            if add_author:
                print >>xml_file, '<author>'
            print >>xml_file, prefix
            if add_author:
                print >>xml_file, '</author>'

        for (part, tag) in zip(parts, ['institution', 'addr-line', 'country']):
            write_tagged(part, tag, xml_file)
        
        print >>xml_file, suffix
        print >>xml_file, '</aff>'

    print >>xml_file, '</affs>'

def get_args():
    parser = argparse.ArgumentParser(description="Export hand-made tags to XML")
    
    parser.add_argument('--xml', default='data/hand-inf.xml')
    parser.add_argument('--txt', default='data/hand-inf.txt')
    parser.add_argument('--author', type=int, default=0)
    
    return parser.parse_args()

if __name__ == '__main__':

    args = get_args()

    text_file = codecs.open(args.txt, 'rb', encoding='utf8')
    xml_file = codecs.open(args.xml, 'wb', encoding='utf8')
    export_tags(text_file, xml_file, args.author == 1)

