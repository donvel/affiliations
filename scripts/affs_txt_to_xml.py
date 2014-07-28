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
import random


def get_args():
    parser = argparse.ArgumentParser(description="Convert txt with xml lines to pure xml.")
    
    parser.add_argument('--input', default='data/affs-parsed.txt')
    parser.add_argument('--output', default='data/affs-parsed.xml')
    parser.add_argument('--with_ids', type=int, default=1)
    parser.add_argument('--shuffle', type=int, default=0)
    parser.add_argument('--only_n', type=int, default=0)
    
    return parser.parse_args()


if __name__ == '__main__':
    random.seed(10101)

    args = get_args()

    input_file = open(args.input, 'rb')
    output_file = open(args.output, 'wb')

    print >>output_file, '<affs>'

    lines = input_file.readlines()

    if args.shuffle == 1:
        random.shuffle(lines)

    if args.only_n != 0:
        lines = lines[:args.only_n]
   
    for line in lines:
        if args.with_ids == 1:
            if not re.match(r'^(\d+) <aff', line):
                print line
                continue
            cline = re.sub(r'^(\d+) <aff', r'<aff num="\1"', line)
            print >>output_file, cline.rstrip()
        else:
            if not re.match(r'^<aff', line):
                print line
                continue
            print >>output_file, line.strip()
    
    print >>output_file, '</affs>'
