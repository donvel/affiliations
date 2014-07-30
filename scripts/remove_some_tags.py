""" Remove some of the <country> and <address> tags,
    so that test / training data is more realistic.
"""

import xml.etree.ElementTree as ET
import argparse
import random

from collections import defaultdict
from utils import print_out


def remove_last_comma(aff):
    last_elem = aff[-1]

    while not last_elem.text or not last_elem.text.strip():
        aff.remove(last_elem)
        last_elem = aff[-1]

    text = last_elem.text.rstrip()
    if text.endswith(','):
        last_elem.text = text[:-1]


def remove_elems(tag, aff):
    for elem in list(aff):
        if elem.tag == tag:
            aff.remove(elem)
    remove_last_comma(aff)


def remove_tags(root, aratio, cratio, acratio):
    for aff in root:
        tags = set([elem.tag for elem in aff])
        if not set(['country', 'addr-line', 'institution']) <= tags:
            print_out(aff) # Tag missing already

        if random.random() <= aratio:
            remove_elems('addr-line', aff)
        elif random.random() <= cratio:
            remove_elems('country', aff)
        elif random.random() <= acratio:
            remove_elems('addr-line', aff)
            remove_elems('country', aff)


def aff_type(aff):
    return tuple(set(el.tag for el in aff))


def make_statistics(root):
    types = defaultdict(int)
    for aff in root:
        types[aff_type(aff)] += 1
    total = len(list(root))
    for key, value in types.items():
        print key, value / float(total)


def get_args():
    parser = argparse.ArgumentParser(description="Remove some tags")
    
    parser.add_argument('--input', default='data/affs-improved.xml')
    parser.add_argument('--output', default='data/affs-real-like.xml')
    parser.add_argument('--address_ratio', type=int, default=7, help='in perc')
    parser.add_argument('--country_ratio', type=int, default=9, help='in perc')
    parser.add_argument('--ac_ratio', type=int, default=2, help='in perc')
    
    return parser.parse_args()


if __name__ == '__main__':
    random.seed(10101)

    args = get_args()

    tree = ET.parse(args.input)
    root = tree.getroot()
    make_statistics(root)
    remove_tags(root, args.address_ratio / 100.0, args.country_ratio / 100.0, args.ac_ratio / 100.0)
    make_statistics(root)
    tree.write(args.output)
