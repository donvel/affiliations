""" Returns a labeling score:
    Let T = sum_(s - an affiliation) (# of labels in the target labeling of s)
    C = sum_s (# of labels l in the target labeling of s such that
        the occurences of l in s are exactly the same in the tested labeling)
    The score equals C / T
"""
import argparse

from collections import defaultdict

def check_labelings(target_lbng, lbng):
    processed = []
    total = 0
    correct = 0
    for label in target_lbng:
        if label not in processed:
            processed += [label]
            target_positions = [x == label for x in target_lbng]
            positions = [x == label for x in lbng]
            total += 1
            if positions == target_positions:
                correct += 1
    return (correct, total)


def get_tokens(hint_file):
    tokens = []
    ctokens = []
    with open(hint_file, 'rb') as hint:
        for line in hint:
            l = line.rstrip()
            if l:
                ctokens += [l]
            else:
                tokens += [ctokens]
                ctokens = []
    return tokens


def print_aff(aff, lb, f):
    extend = {'INST': 'institution', 'ADDR': 'addr-line', 'COUN': 'country'}
    last_label = 'NONE'

    print >>f, '<aff>'

    for (word, l) in zip(aff, lb):
        if l != last_label:
            if last_label != 'NONE':
                f.write('</%s>' % extend[last_label])
            if l != 'NONE':
                f.write('<%s>' % extend[l])

            last_label = l
        f.write(word + ' ')

    if last_label != 'NONE':
        f.write('</%s>' % extend[last_label])

    print >>f, '</aff>'


def show_labels(labeling, hint_file, output_file, only_errors=False):
    tokens = get_tokens(hint_file)
    assert len(labeling) == len(tokens)
    with open(output_file, 'wb') as f:


        print >>f, "<affs>"

        for (aff, (lb_t, lb2)) in zip(tokens, labeling):
        
            assert len(aff) == len(lb_t)
            
            if not only_errors or lb_t != lb2:

                print_aff(aff, lb_t, f)
                print_aff(aff, lb2, f)

                print >>f, "<br>"

        print >>f, "</affs>"


def group_type(labeling):
    return tuple(set(l for l in labeling if l != 'NONE'))


def read_file(filename, hint_file, error_file, label_file, one_number):
    with open(filename, 'rb') as f:
        t_lbng = []
        lbng = []

        correct = 0.0
        total = 0.0

        group_correct = defaultdict(int)
        group_total = defaultdict(int)

        at = 0.0
        ac = 0.0
        best = 0.0
        group_best = []

        best_labeling = []
        c_labeling = []

        for line in f:
            tokens = line.split()
            if len(tokens) == 0: # Next affiliation
                (c, t) = check_labelings(t_lbng, lbng)
                c_labeling += [(t_lbng, lbng)]
                correct += c
                total += t

                group_correct[group_type(t_lbng)] += t_lbng == lbng
                group_total[group_type(t_lbng)] += 1

                ac += t_lbng == lbng
                at += 1

                t_lbng = []
                lbng = []
            elif len(tokens) == 1: # Joint score, next test
                f1 = float(tokens[0])
                score = correct / total
                if score > best:
                    best = score
                    group_best = (group_correct, group_total)
                    best_labeling = c_labeling
                c_labeling = []

                if not one_number:
                    print 'S: %f, F1: %f, GA: %f' % \
                            (score, f1, ac / at)

                group_correct = defaultdict(int)
                group_total = defaultdict(int)

                correct = 0.0
                total = 0.0
                ac = 0.0
                at = 0.0
            else: # (target, given)
                assert len(tokens) == 2
                t_lbng += [tokens[0]]
                lbng += [tokens[1]]

        print 'max score: %f, score after training %f' % (best, score)
       
        group_correct, group_total = group_best
        for key in group_total:
            print 'score %f, total %d, correct %d, %r' % \
                    (group_correct[key] / float(group_total[key]),
                            group_total[key], group_correct[key], key)

        show_labels(best_labeling, hint_file, error_file, only_errors=True)
        show_labels(best_labeling, hint_file, label_file)


def get_args():
    parser = argparse.ArgumentParser(description="Count score and generate error file")
    
    parser.add_argument('--input_file', default='crfdata/acrf_output_Testing.txt')
    parser.add_argument('--hint_file', default='crfdata/default-hint.txt')
    parser.add_argument('--error_file', default='crfdata/default-err.xml')
    parser.add_argument('--label_file', default='crfdata/default-label.xml')
    parser.add_argument('--one_number', type=int, default=0)
    
    return parser.parse_args()



if __name__ == '__main__':

    args = get_args()

    read_file(args.input_file, args.hint_file, args.error_file,
            args.label_file, args.one_number == 1)
