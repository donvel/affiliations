""" Split an XML file into two parts (for training and testing) """

import xml.etree.ElementTree as ET
import argparse
import random

from utils import print_out


def write_tree(affs, filename):
    f = open(filename, 'wb')
    print >>f, '<affs>'
    
    for aff in affs:
        print_out(aff, where=f)
    
    print >>f, '</affs>'


def get_args():
    parser = argparse.ArgumentParser(description="Export tokens to crf format")
    
    parser.add_argument('--train', default='data/improved-train.xml')
    parser.add_argument('--test', default='data/improved-test.xml')
    parser.add_argument('--input', default='data/affs-improved.xml')
    parser.add_argument('--split_point', type=int, default=4000)
    parser.add_argument('--number', type=int, default=1600)
    parser.add_argument('--cross', type=int, default=0)
    parser.add_argument('--part', type=int, default=1)
    parser.add_argument('--parts', type=int, default=5)
    
    return parser.parse_args()


if __name__ == '__main__':
    random.seed(10101)

    args = get_args()

    affs = list(ET.parse(args.input).getroot())
    random.shuffle(affs)

    if args.cross == 1:
        test_from = (args.part - 1) * args.number
        test_to = args.part * args.number
        test_train_to = args.parts * args.number
        
        affs_train = affs[:test_from] + affs[test_to:test_train_to]
        affs_test = affs[test_from:test_to]
        
        write_tree(affs_train, args.train)
        write_tree(affs_test, args.test)
    else:

        write_tree(affs[:args.split_point], args.train)
        write_tree(affs[args.split_point:], args.test)

        print len(affs)
