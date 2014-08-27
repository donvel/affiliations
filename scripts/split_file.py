import random
import argparse

def get_id(line):
    return line.split()[0]


def omit_ids(lines, id_file):
    used_ids = set(get_id(l) for l in open(id_file, 'rb'))
    return [l for l in lines if get_id(l) not in used_ids]


def get_args():
    parser = argparse.ArgumentParser(description="Get some lines from the file, "
            "omit the ones used in the training set")
    
    parser.add_argument('--inname', default='data/raw-affs-bio.txt')
    parser.add_argument('--outname', default='data/raw-bio.txt')
    parser.add_argument('--how_many', type=int, default=100)
    parser.add_argument('--omit_ids', type=int, default=1)
    parser.add_argument('--used_ids', default='data/affs-string.txt')

    return parser.parse_args()

NUM_LEN = len('2740170 ') # Assume all ids look like this

if __name__ == '__main__':
    random.seed(10101)
    args = get_args()

    with open(args.inname, 'rb') as fin:
        with open(args.outname, 'wb') as fout:
            lines = fin.readlines()
            if args.omit_ids == 1:
                lines = omit_ids(lines, args.used_ids)
            random.shuffle(lines)
            lines = lines[:args.how_many]
            for l in lines:
                l = l.rstrip()
                if args.omit_ids == 1:
                    l = l[NUM_LEN:]
                print >>fout, l
                print >>fout

