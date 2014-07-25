""" Convert a file of the form:
    DOC_ID1 <aff> something1 </aff>
    DOC_ID2 <aff> something2 </aff>
    ...
    to
    <affs>
    <aff num="DOC_ID1"> something1 </aff>
    <aff num="DOC_ID2"> something2 </aff>
    ...
    </affs>

    so it becomes a valid XML
"""

import re
import argparse


def get_args():
    parser = argparse.ArgumentParser(description="Convert txt with xml lines to pure xml.")
    
    parser.add_argument('--input', default='data/affs-parsed.txt')
    parser.add_argument('--output', default='data/affs-parsed.xml')
    
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()

    input_file = open(args.input, 'rb')
    output_file = open(args.output, 'wb')

    print >>output_file, '<affs>'
   
    for line in input_file:
        if not re.match(r'^(\d+) <aff', line):
            print line
            continue
        cline = re.sub(r'^(\d+) <aff', r'<aff num="\1"', line)
        print >>output_file, cline.rstrip()
    
    print >>output_file, '</affs>'
