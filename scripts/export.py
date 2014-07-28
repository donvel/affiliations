""" Export tagged affiliations XML to CRF input (feature extraction)
"""

import xml.etree.ElementTree as ET
import unicodedata
import ast
import codecs
import argparse
import random

from collections import defaultdict
from utils import normalize, tokenize, text_in_element, to_unicode, glue_lists


DICTS_DIR = 'dicts/'


AVAILABLE_FEATURES = [
        'Word',
        'UpperCase',
        'AllUpperCase',
        'Number',
        # 'AlphaNum', doesn't apply to the current tokenizing method
        'Punct',
        'WeirdLetter',
        'Freq',
        'Rare',
        'Length',

        # dict - based
        'StopWord',
        'Country',
        'Address',
    ]


features_on = []
dicts = {}
rare_thr = 2 # Rare <=> at most rare_thr occurences in the training set
nei_thr = 0 # Copy neighbours' features in this range


def dict_from_file(filename):
    d = defaultdict(list)
    with codecs.open(DICTS_DIR + filename, 'rb', encoding='utf8') as f:
        for line in f:
            tokens = [normalize(t) for t in tokenize(line)]
            for (nb, token) in enumerate(tokens):
                d[token] += [(tokens, nb)]
        return d


def load_dicts(dd):
    what_where = [
            ('StopWord', 'stop_words_short.txt'),
            ('Country', 'countries.txt'),
            ('Address', 'address_keywords.txt'),
        ]

    for (what, where) in what_where:
        if what in features_on:
            dd[what] = dict_from_file(where)


def all_upper_case(word):
    return all(c.isupper() for c in word)


def first_upper_case(word): # Mr and M but not MR, makes sense ???
    return word[0].isupper() and not any(c.isupper() for c in word[1:])


def get_local_features(token, word_freq=None):

    assert len(token) >= 1

    features = []
    
    ntoken = normalize(token)

    if token.isalpha():

        if 'UpperCase' in features_on:
            if first_upper_case(token):
                features += ['UpperCase']

        if 'AllUpperCase' in features_on:
            if all_upper_case(token):
                features += ['AllUpperCase']

        if 'Freq' in features_on:
            features += ['Freq:%s' % str(word_freq[ntoken])]
        
        if 'Rare' in features_on:
            if word_freq[ntoken] <= rare_thr:
                features += ['Rare']

    elif token.isdigit():

        if 'Number' in features_on:
            features += ['Number']

    elif token.isalnum():

        if 'AlphaNum' in features_on:
            features += ['AlphaNum']

    elif len(to_unicode(token)) == 1:

        if unicodedata.category(to_unicode(token)) == 'Po':
            if 'Punct' in features_on:
                features += ['Punct']
        else:
            if 'WeirdLetter' in features_on:
                features += ['WeirdLetter']
    
    if 'Word' in features_on:
        if not any(x in features for x in ['Rare', 'Number', 'AlphaNum']):
            features += ['W=%s' % normalize(token, lowercase=False)]

    if 'Length' in features_on:
        features += ['Length:%s' % str(len(token))]

    return features


def matches((l1, p1), (l2, p2)):
    """ True for (['Kot', 'je', 'mysz', 'dzis'], 3), (['mysz', 'dzis'], 1) """
    offset = p1 - p2
    return l1[offset:offset+len(l2)] == l2


def get_dict_features(token_list):
    token_list = [normalize(t) for t in token_list]
    features = []
    for (nb, token) in enumerate(token_list):
        cfeatures = []
        for (feature, d) in dicts.items():
            possible_hits = d[token]
            for phit in possible_hits:
                if matches((token_list, nb), phit):
                    cfeatures += [feature]
                    break
        features += [cfeatures]
    return features


def find_word_freq(li):
    all_tokens = [normalize(t)
             for aff in li
             for t in tokenize(text_in_element(aff))]
    freq = defaultdict(int)
    for token in all_tokens:
        freq[token] += 1
    return freq


def get_nei_features(features):
    nei_features = []
    for i in range(len(features)):
        cfeatures = []

        for j in range(-nei_thr, nei_thr + 1):
            if j == 0:
                continue
            k = i + j
            nfeatures = []
            if k < 0:
                nfeatures = ['Start']
            elif k >= len(features):
                nfeatures = ['End']
            else:
                nfeatures = features[k]
            cfeatures += [f + '@' + str(j) for f in nfeatures]

        nei_features += [cfeatures]

    return nei_features


def get_timesteps(token_list, word_freq=None):
    local_features = [get_local_features(t, word_freq=word_freq) for t in token_list]
    dict_features = get_dict_features(token_list)

    features = [glue_lists(fts) for fts in zip(local_features, dict_features)]

    nei_features = get_nei_features(features)
    features = [glue_lists(fts) for fts in zip(features, nei_features)]

    return features


def get_labels(text, label):
    return [(t, label) for t in tokenize(text)]


def create_instance(aff, f, word_freq=None, hint_file=None):
    full_text = text_in_element(aff)
    token_list = tokenize(full_text)


    labeled_list = []
    labeled_list += get_labels(aff.text, 'NONE')
    for item in aff:
        labeled_list += get_labels(item.text, item.tag.upper()[:4])
        labeled_list += get_labels(item.tail, 'NONE')

    token_list2, label_list = zip(*labeled_list)

    assert token_list == list(token_list2), \
            '%r %r' % (token_list, token_list2) # If not, the training data may be faulty

    time_steps = get_timesteps(token_list, word_freq=word_freq)
    for (label, features) in zip(label_list, time_steps):
        print >> f, '%s ---- %s' % (label, ' '.join(features))
    
    if hint_file:
        for token in token_list:
            print >> hint_file, token.encode('utf8')


def create_input(li, f, h, word_freq=None):
    for aff in li:
        create_instance(aff, f, word_freq=word_freq, hint_file=h)
        print >> f
        if h:
            print >> h


def export_to_crf_input(input_file, test_input, num1, num2, file1, file2, hint_file):
    tree = ET.parse(input_file)
    affs = list(tree.getroot())
    random.shuffle(affs)

    if test_input:
        test_tree = ET.parse(test_input)
        test_affs = list(test_tree.getroot())
        random.shuffle(test_affs)
        
        assert num1 <= len(affs) and num2 <= len(test_affs)
        test_affs = affs[:num2]
    else:
        assert num1 + num2 <= len(affs)
        test_affs = affs[num1:num1 + num2]
    
    train_affs = affs[:num1]

    aff_list = [(train_affs, file1, None), (test_affs, file2, hint_file)]
    
    word_freq = set([])
    if any(x in features_on for x in ['Rare', 'Freq']):
        word_freq=find_word_freq(train_affs)

    for (li, f, h) in aff_list:
        create_input(li, f, h, word_freq)


def get_args():
    parser = argparse.ArgumentParser(description="Export tokens to crf format")
    
    parser.add_argument('features', default='[]', help="Python list eg. '[\"Word\"]'")
    parser.add_argument('--train_number', type=int, default=100)
    parser.add_argument('--test_number', type=int, default=1000)
    parser.add_argument('--train', dest='train_file', default='crfdata/default-train.crf')
    parser.add_argument('--test', dest='test_file', default='crfdata/default-test.crf')
    parser.add_argument('--hint', dest='hint_file', default='crfdata/default-hint.txt')
    parser.add_argument('--input', dest='input_file', default='data/affs-improved.xml')
    parser.add_argument('--input_test', dest='input_test_file', default=None,
            help="Specify a separate file with test data")
    parser.add_argument('--rare', type=int, default=2)
    parser.add_argument('--neighbor', type=int, default=0)
    
    return parser.parse_args()


if __name__ == '__main__':
    random.seed(10101)

    args = get_args()

    features_on = ast.literal_eval(args.features)
    assert set(features_on) <= set(AVAILABLE_FEATURES)
    rare_thr = args.rare
    nei_thr = args.neighbor

    print features_on
    train_file = open(args.train_file, 'wb')
    test_file = open(args.test_file, 'wb')
    hint_file = open(args.hint_file, 'wb')

    load_dicts(dicts)
    export_to_crf_input(args.input_file, args.input_ test_file, \
            args.train_number, args.test_number, \
            train_file, test_file, hint_file)
