"""
f1 -- average of f1 scores for all labels

matched -- avarage of partially correct labeling over the label types: ADDR, COUN, INST
    (example: target = AAIIC, then AAAIC is partially correct for COUN, but not for ADDR or INST)

success -- average of completely correct labelings over possible affiliation types:
    (ADDR, COUN, INST), (COUN, INST), (ADDR, INST), (INST)

total success -- amount of completely correct labelings
"""
import argparse
import sys

from collections import defaultdict


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


def aff_type(labeling):
    return tuple(sorted(list(set(l for l in labeling if l != 'NONE'))))


class Score:

    def __init__(self):
        self.labels = ['ADDR', 'COUN', 'INST']
        self.types = [('INST',), ('ADDR', 'INST'), ('COUN', 'INST'), ('ADDR', 'COUN', 'INST')]

        self.confusion = dict(((l1, l2), 0) for l1 in self.labels for l2 in self.labels)
        self.precision = dict((l, 0) for l in self.labels)
        self.recall = dict((l, 0) for l in self.labels)
        self.f1 = dict((l, 0) for l in self.labels)
        self.f1_mean = 0
        
        self.type_correct = dict((t, 0) for t in self.types)
        self.type_total = dict((t, 0) for t in self.types)
        self.success = dict((t, 0) for t in self.types)
        self.success_mean = 0
        self.success_wmean = 0

        self.label_correct = dict((l, 0) for l in self.labels)
        self.label_total = dict((l, 0) for l in self.labels)
        self.matched = dict((l, 0) for l in self.labels)
        self.matched_mean = 0

        self.labeling = []

    def update(self, t_lbng, lbng):

        self.labeling += [(t_lbng, lbng)]

        # Ignore NONE
        filtered = [(t, p) for (t, p) in zip(t_lbng, lbng) if t != 'NONE']
        t_lbng, lbng = zip(*filtered)

        for (target, given) in zip(t_lbng, lbng):
            self.confusion[(target, given)] += 1

        all_tags = aff_type(t_lbng)
        
        self.type_correct[all_tags] += t_lbng == lbng
        self.type_total[all_tags] += 1

        for label in all_tags:
            target_positions = [x == label for x in t_lbng]
            positions = [x == label for x in lbng]
            self.label_correct[label] += positions == target_positions
            self.label_total[label] += 1

    def calculate(self):
    
        for l in self.labels:
            retrieved = sum(self.confusion[(x, l)] for x in self.labels)
            relevant = sum(self.confusion[(l, x)] for x in self.labels)
            rel_ret = self.confusion[(l, l)]
            self.precision[l] = rel_ret / float(retrieved)
            self.recall[l] = rel_ret / float(relevant)
            prec, rec = self.precision[l], self.recall[l]
            self.f1[l] = 2 * prec * rec / (prec + rec)

        self.f1_mean = sum(self.f1[l] for l in self.labels) / len(self.labels)

        for t in self.types:
            if self.type_total[t] != 0:
                self.success[t] = self.type_correct[t] / float(self.type_total[t])
            else:
                self.success[t] = 1.0

        self.success_mean = sum(self.success[t] for t in self.types) / len(self.types)
        self.success_wmean = (sum(self.type_correct[t] for t in self.types)
                / float(sum(self.type_total[t] for t in self.types)))

        for l in self.labels:
            self.matched[l] = self.label_correct[l] / float(self.label_total[l])

        self.matched_mean = sum(self.matched[l] for l in self.labels) / len(self.labels)

    def write(self, where=sys.stdout):
        print >>where, 'f1: %f, success: %f, matched: %f' % \
                (self.f1_mean, self.success_mean, self.matched_mean)


    def full_write(self):
        
        HELP_TEXT = """
1) global statistics
f1 -- the mean of F1 scores of all label types
success -- the mean of "success scores" of all affiliation types
mathed -- the mean of "matched scores" of all label types

total success -- the fraction of the affiliation strings which were labeled 100% correctly

2) Confusion Matrix format:

        PREDICTED1 PREDICTED2
ACTUAL1
ACTUAL2

3) SUCCESS -- the fraction of the affiliation strings which were labeled 100% correctly.

This factor is computed separately for different affiliation kinds.
There are four kinds of affiliations, depending on whether they
contain "address" and "country" parts.

4) MATCHED -- this factor is computed separately for different label types.
For a given label type X, this is the ratio of affiliation strings in which
tokens predicted to be X were exactly the actual X-type tokens.
"""

        print
        self.write()
        print 'total success: %f' % self.success_wmean

        print
        print 10 * '=' + ' CONFUSION ' + 10 * '='
        for l1 in ['name'] + self.labels:
            for l2 in ['name'] + self.labels + ['PREC', 'REC ', 'F1  ']:
                if l1 == 'name' and l2 == 'name':
                    sys.stdout.write(9 * ' ')
                elif l1 == 'name':
                    sys.stdout.write(l2 + 4 * ' ')
                elif l2 == 'name':
                    sys.stdout.write(l1 + 2 * ' ')
                elif l2 == 'PREC':
                    sys.stdout.write('%.5f ' % self.precision[l1])
                elif l2 == 'REC ':
                    sys.stdout.write('%.5f ' % self.recall[l1])
                elif l2 == 'F1  ':
                    sys.stdout.write('%.5f ' % self.f1[l1])
                else:
                    sys.stdout.write('%7.1d ' % self.confusion[l1, l2])
                    if l2 == 'INST':
                        sys.stdout.write(2 * ' ')
            print
        
        print
        print 10 * '=' + ' SUCCESS ' + 10 * '='
        print "RATIO     CORRECT  TOTAL  TYPE"
        for key, value in self.success.items():
            print '%.5f %7.1d %7.1d %r' % \
                    (value, self.type_correct[key], self.type_total[key], key)

        print
        print 10 * '=' + ' MATCHED ' + 10 * '='
        for key, value in self.matched.items():
            print '%.5f %r' % (value, key)

        print
        print 10 * '-' + ' DESCRIPTION ' + 10 * '-'
        print HELP_TEXT


    def serialize(self):
        for l1 in self.labels:
            for l2 in self.labels:
                print self.confusion[(l1, l2)]

        for t in self.types:
            print self.type_correct[t]
            print self.type_total[t]

        for l in self.labels:
            print self.label_correct[l]
            print self.label_total[l]


    def deserialize(self, files):
        for fname in files:
            with open(fname, 'rb') as f:
                for l1 in self.labels:
                    for l2 in self.labels:
                        self.confusion[(l1, l2)] += int(f.readline())

                for t in self.types:
                    self.type_correct[t] += int(f.readline())
                    self.type_total[t] += int(f.readline())

                for l in self.labels:
                    self.label_correct[l] += int(f.readline())
                    self.label_total[l] += int(f.readline())


def read_file(filename, hint_file, error_file, label_file, full_output):
    with open(filename, 'rb') as f:
        t_lbng, lbng = [], []

        score = Score()
        best_score = Score()
        last_score = None

        for line in f:
            tokens = line.split()
            if len(tokens) == 0: # Next affiliation
                score.update(t_lbng, lbng)
                t_lbng, lbng = [], []
            elif len(tokens) == 1: # Joint score, next test
                score.calculate()
                if full_output:
                    score.write()
                if score.matched_mean > best_score.matched_mean:
                    best_score = score
                last_score = score
                score = Score()
            else: # (target, given)
                assert len(tokens) == 2
                t_lbng += [tokens[0]]
                lbng += [tokens[1]]

        if full_output:
            print '==================== BEST SCORE =========================='
            best_score.write()
            print '==================== LAST SCORE =========================='
            last_score.write()
            last_score.full_write()
           
            show_labels(last_score.labeling, hint_file, error_file, only_errors=True)
            show_labels(last_score.labeling, hint_file, label_file)
        else:
            last_score.write(sys.stderr)
            last_score.serialize()


def get_args():
    parser = argparse.ArgumentParser(description="Count score and generate error file")
    
    parser.add_argument('--input_file', default='crfdata/acrf_output_Testing.txt')
    parser.add_argument('--hint_file', default='crfdata/default-hint.txt')
    parser.add_argument('--error_file', default='crfdata/default-err.xml')
    parser.add_argument('--label_file', default='crfdata/default-label.xml')
    parser.add_argument('--full_output', type=int, default=0)
    
    return parser.parse_args()


if __name__ == '__main__':

    args = get_args()

    read_file(args.input_file, args.hint_file, args.error_file,
            args.label_file, args.full_output == 1)
