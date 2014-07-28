""" Remove some of the <country> and <address> tags,
    so that test / training data is more realistic.
"""

import xml.etree.ElementTree as ET
import argparse
import random

from utils import print_out


def remove_last_comma(aff):
    last_elem = aff[-1]

    while not last_elem.text or not last_elem.text.strip():
        aff.remove(last_elem)
        last_elem = aff[-1]

    text = last_elem.text.rstrip()
    if text.endswith(','):
        last_elem.text = text[:-1]


def remove_tags(root, aratio, cratio):
    for aff in root:
        tags = set([elem.tag for elem in aff])
        if not set(['country', 'addr-line', 'institution']) <= tags:
            print_out(aff) # Tag missing already

        if random.random() <= aratio:
            for elem in list(aff):
                if elem.tag == 'addr-line':
                    aff.remove(elem)

        if random.random() <= cratio:
            for elem in list(aff):
                if elem.tag == 'country':
                    aff.remove(elem)
            remove_last_comma(aff)


def get_args():
    parser = argparse.ArgumentParser(description="Remove some tags")
    
    parser.add_argument('--input', default='data/affs-improved.xml')
    parser.add_argument('--output', default='data/affs-real-like.xml')
    parser.add_argument('--address_ratio', type=int, default=5, help='in perc')
    parser.add_argument('--country_ratio', type=int, default=8, help='in perc')
    
    return parser.parse_args()


if __name__ == '__main__':
    random.seed(10101)

    args = get_args()

    tree = ET.parse(args.input)
    root = tree.getroot()
    remove_tags(root, args.address_ratio / 100.0, args.country_ratio / 100.0)
    tree.write(args.output)
