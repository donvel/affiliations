""" Remove unnecessary tags """

import xml.etree.ElementTree as ET
import argparse


keep_tags = ['addr-line', 'institution', 'country']
label_tags = ['label', 'bold', 'sup']
replace_tags = {'break': ' '}


def addstr(str1, str2):
    return (str1 or '') + (str2 or '')


def getstr(item):
    text = replace_tags.get(item.tag, None) or item.text
    return addstr(text, item.tail)


def is_label(item):
    """ eg. <sup>2</sup> """
    return item.tag in label_tags and len(item.text) <= 2


def strip_tags(root):
    """ Remove tags like <italic>, labels like <sup>, replace <break\> with spaces """
    for aff in list(root):
        last_item = None

        for item in list(aff):

            # Expand children
            for item2 in list(item):
                my_text = getstr(item2)
                item.text = addstr(item.text, my_text)
                for item3 in list(item2):
                    raise Exception("To deep (level 3)")
                item.remove(item2)

            if item.tag not in keep_tags:
                my_text = None
                if (last_item is None and is_label(item)):
                    # We don't need the text content
                    my_text = item.tail
                else:
                    my_text = getstr(item)

                if last_item is not None:
                    last_item.tail = addstr(last_item.tail, my_text)
                else:
                    aff.text = addstr(aff.text, my_text)

                aff.remove(item)

            else:
                last_item = item


def get_args():
    parser = argparse.ArgumentParser(description="Remove unnecessary tags")
    
    parser.add_argument('--input', default='data/affs-parsed.xml')
    parser.add_argument('--output', default='data/affs-stripped.xml')
    
    return parser.parse_args()


if __name__ == '__main__':
    
    args = get_args()

    tree = ET.parse(args.input)
    root = tree.getroot()
    strip_tags(root)
    tree.write(args.output)



