""" Export tagged affiliations XML to CRF input (feature extraction)
"""

import xml.etree.ElementTree as ET
import unicodedata
import ast
import codecs
import argparse
import random
import operator

from collections import defaultdict
from utils import normalize, tokenize, text_in_element, to_unicode, glue_lists, \
        is_punct, create_xml_tree, print_out


DICTS_DIR = 'dicts/'


AVAILABLE_FEATURES = [
        'Word',
        'IsWord',
        'Number',
        'UpperCase',
        'AllUpperCase',
        'AllLowerCase',
        'AlphaNum', # does not apply to one tokenizing method
        'Separator',
        'NonAlphanum',
        'Length',
        # 'Freq', # Irrelevant
        'Rare',

        # dict - based
        'Country',
        'StopWord',
        'StopWordEng',
        'Address',
        'State',
        'StateCode',
        'City',
        'Institution', # WARNING - used also for test / training data generation!
    ]


features_on = []
dicts = {}
rare_thr = 2 # Rare <=> at most rare_thr occurences in the training set
nei_thr = 0 # Copy neighbours' features in this range
split_alphanum = False # Should alphanumeric words be split into many parts

def dict_from_file(filename, match_case=True):
    d = defaultdict(list)
    with codecs.open(DICTS_DIR + filename, 'rb', encoding='utf8') as f:
        for line in f:
            tokens = tokenize(normalize(line, lowercase=(not match_case)),
                    split_alphanum=split_alphanum)
            for (nb, token) in enumerate(tokens):
                d[token] += [(tokens, nb)]
        return (d, match_case)


def load_dicts(dd):
    what_where = [
            ('Address', 'address_keywords.txt', False),
            ('City', 'cities.txt', True),
            ('Country', 'countries2.txt', True),
            ('Institution', 'institution_keywords.txt', False),
            ('State', 'states.txt', True),
            ('StateCode', 'state_codes.txt', True),
            ('StopWordEng', 'stop_words_short.txt', False),
            ('StopWord', 'stop_words_multilang.txt', False),
        ]

    for (what, where, match_case) in what_where:
        if what in features_on:
            dd[what] = dict_from_file(where, match_case)

def all_lower_case(word):
    return all(c.islower() for c in word)

def all_upper_case(word):
    return all(c.isupper() for c in word)


def first_upper_case(word): # Mr and M but not MR, makes sense ???
    return word[0].isupper() and not any(c.isupper() for c in word[1:])


def get_local_features(token, word_freq=None):

    assert len(token) >= 1

    features = []
    
    ntoken = normalize(token, lowercase=False)

    if token.isalpha():

        if 'UpperCase' in features_on:
            if first_upper_case(ntoken):
                features += ['IsUpperCase']

        if 'AllUpperCase' in features_on:
            if all_upper_case(ntoken):
                features += ['IsAllUpperCase']

        if 'AllLowerCase' in features_on:
            if all_lower_case(ntoken):
                features += ['IsAllLowerCase']

        if 'Freq' in features_on:
            features += ['Freq:%s' % str(word_freq[ntoken])]
        
        if 'Rare' in features_on:
            if word_freq[ntoken] <= rare_thr:
                features += ['IsRare']

        if 'IsWord' in features_on:
            features += ['IsWord']

    elif token.isdigit():

        if 'Number' in features_on:
            features += ['IsNumber']

    elif token.isalnum():

        if 'AlphaNum' in features_on:
            features += ['IsAlphaNum']

    elif len(to_unicode(token)) == 1:

        if is_punct(token):
            if 'Separator' in features_on:
                features += ['IsSeparator']
        else:
            if 'NonAlphanum' in features_on:
                features += ['IsNonAlphanum']
    
    if 'Word' in features_on:
        if not any(x in features for x in ['IsNumber', 'IsAlphaNum']):
            features += ['W=%s' % ntoken]

    if 'Length' in features_on:
        features += ['Length:%s' % str(len(ntoken))]

    return features


def matches((l1, p1), (l2, p2), match_case=True):
    """ True for (['Kot', 'je', 'mysz', 'dzis'], 3), (['mysz', 'dzis'], 1) """
    offset = p1 - p2
    li1 = l1[offset:offset+len(l2)]
    li2 = l2
    if not match_case:
        li1 = [t.lower() for t in li1]
        li2 = [t.lower() for t in li2]
    return li1 == li2


def get_dict_features(token_list):
    token_list = [normalize(t, lowercase=False) for t in token_list]
    features = []
    for (nb, token) in enumerate(token_list):
        cfeatures = []
        for (feature, (d, match_case)) in sorted(dicts.items(),
                key=operator.itemgetter(0)):
            possible_hits = d[token if match_case else token.lower()]
            for phit in possible_hits:
                if matches((token_list, nb), phit, match_case=match_case):
                    cfeatures += ['Keyword' + feature]
                    break
        features += [cfeatures]
    return features


def find_word_freq(li):
    all_tokens = [normalize(t, lowercase=False)
             for aff in li
             for t in tokenize(text_in_element(aff),
                 split_alphanum=split_alphanum)]
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
    return [(t, label) for t in tokenize(text, split_alphanum=split_alphanum)]


def create_instance(aff, f, word_freq=None, hint_file=None):
    full_text = text_in_element(aff)
    token_list = tokenize(full_text, split_alphanum=split_alphanum)


    labeled_list = []
    labeled_list += get_labels(aff.text, 'TEXT') #TODO is it OK?
    for item in aff:
        labeled_list += get_labels(item.text, item.tag.upper()[:4])
        labeled_list += get_labels(item.tail, 'TEXT') #TODO is it OK?

    token_list2, label_list = zip(*labeled_list)

    if not token_list == list(token_list2):
        print '%r %r' % (token_list, token_list2)

    time_steps = get_timesteps(token_list2, word_freq=word_freq)
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


def add_mock_label(f):
    print >> f, 'TEXT ----'
    print >> f


def export_to_crf_input(tree, test_input, num1, num2, file1, file2, hint_file,
        shuffle=True, mock_label=False):
    affs = list(tree.getroot())
    if shuffle:
        random.shuffle(affs)

    if test_input:
        test_tree = ET.parse(test_input)
        test_affs = list(test_tree.getroot())
        if shuffle:
            random.shuffle(test_affs)
        
        assert num1 <= len(affs) and num2 <= len(test_affs), "train num = %d, test num = %d" % (len(affs), len(test_affs))
        test_affs = test_affs[:num2]
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

    if mock_label:
        add_mock_label(file1)

    return word_freq


def get_args():
    parser = argparse.ArgumentParser(description="Export tokens to crf format")
    
    parser.add_argument('features', default='[]', help="Python list eg. '[\"Word\"]'")
    parser.add_argument('--train_number', type=int, default=100)
    parser.add_argument('--test_number', type=int, default=1000)
    parser.add_argument('--train', dest='train_file', default='crfdata/default-train.crf')
    parser.add_argument('--test', dest='test_file', default='crfdata/default-test.crf')
    parser.add_argument('--hint', dest='hint_file', default='crfdata/default-hint.txt')
    parser.add_argument('--input', dest='input_file', default='data/affs-real-like.xml')
    parser.add_argument('--common_words', default='crfdata/default-common-words.txt')
    parser.add_argument('--input_test', dest='input_test_file', default=None,
            help="Specify a separate file with test data")
    
    parser.add_argument('--rare', type=int, default=2)
    parser.add_argument('--neighbor', type=int, default=0)
    parser.add_argument('--split_alphanum', type=int, default=1)
    parser.add_argument('--xml_input', type=int, default=1)
    parser.add_argument('--shuffle', type=int, default=1)
    parser.add_argument('--mock_text_label', type=int, default=0)
    
    return parser.parse_args()


def write_word_freq(word_freq, threshold, f):
    common_words = []
    for (word, occ) in word_freq.items():
        if occ > threshold and word.isalpha():
            common_words += [word]

    for word in sorted(common_words):
        print >> f, word


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
    word_file = open(args.common_words, 'wb')

    split_alphanum = args.split_alphanum == 1
    xml_input = args.xml_input == 1

    if xml_input:
        tree = ET.parse(args.input_file)
    else:
        tree = create_xml_tree(args.input_file)

    load_dicts(dicts)
    word_freq = export_to_crf_input(tree, args.input_test_file, \
            args.train_number, args.test_number, \
            train_file, test_file, hint_file,
            shuffle=(args.shuffle == 1),
            mock_label=(args.mock_text_label == 1))

    write_word_freq(word_freq, rare_thr, word_file)
