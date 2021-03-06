Affiliation parsing CRF prototype
=================================

We use Python 2.7.5

Data preparation
----------------

#. We want to convert the tagged affiliations in *data/affs-parsed.txt* to valid XML.
   The script will print out invalid entries::

    scripts/affs_txt_to_xml.py

#. Then, we want to get rid off unnecessary tags (like *<italic>*)::

    scripts/strip_tags.py

#. Later, we want to tag the raw text in *data/affs-string.txt* by matching them
   with the tagged affiliations. The script will report how many lines got matched::

    scripts/match_text.py

#. We use a couple of rules to correct some common mistakes in tagging. For that
   we use *improve_data.py*. Some entries get rejected during this stage due to
   untagged content. They will be printed to stdout by the script.::

    scripts/improve_data.py

#. Another thing to do is to remove some of the tagged parts, so the
   training / test data is more realistic.::

    scripts/remove_some_tags.py

   We remove them so that the fractions of affiliation types are more less
   the same as in *data/sample-raw-affs.xml*, statistics for a 200 sample
   from the file can be found in *docs/raw_stats.txt*.

#. To browse the created dataset one may visualize it with::

    scripts/make_readable.py
    firefox data/affs-real-like.html &

#. (Optionally) You may want to split data into two files for training and
   testing. However, you may also keep all your data in one file, and
   the *export.py* script may split it later for you::

    scripts/split_data.py

#. (Optionally) You may want to add authors to some of the affiliations::

    scripts/add_authors.py

   We use the authros from *data/auths.txt*. We generated a 2000-entry
   training file *data/affs-auth.xml*, the fractions of author patterns
   (no author, "X", "X and X", "X, X, X" etc.) were adapted from
   *data/hand-inf.xml*.

CRF training and evaluation
---------------------------

#. Choose the features you want to export and create the crf input files for
   training and testing. The only positional argument of the exporting script
   is a string representing a Python list. So you may invoke it like::

    scripts/export.py --train_number 1000 --test_number 5000 --neighbor 2 --rare 12 '["Word", "UpperCase", "AllUpperCase", "Number", "Separator", "Rare", "Country"]'

   It creates a hint file, which is later used for the score counting.

#. To perform the actual training, you need to install and modify MALLET GRMM.
   Download grmm-0.1.3.tar.gz from http://mallet.cs.umass.edu/grmm/download.php
   and extract it to *grmm*. Then move the files in *grmm_custom* to corresponding
   directories in *grmm*::

    cd grmm_custom
    cp --parents src/edu/umass/cs/mallet/grmm/learning/ACRFTrainer.java ../grmm
    cd ../grmm
    make

#. Now you may use the *train.sh* script::

    ./train.sh training_data_size neighbor_feature_range rare_threshold split_alphanum 'features_list' training_name

   for example::

    ./train.sh 100 0 0 1 '["Word"]' test

   The following things will happen:

   #. *export.py* will be called with appropriate arguments
   #. The CRF diagnostic output will be redirected to *log\err_*.txt*
   #. *count_score.py* will calculate the labeling accuracy based on
      *crfdata/acrf_output** (created during the CRF training) and the hint
      file
   #. All the incorrect labelings will be displayed in Firefox.

#. To cross validation you may use the *cross_validate.sh* shell
   script. For example to perform a 5-fold cross validation using 8000
   affiliations, type::

    ./cross_validate.sh 8000 5 my_cute_cross_validation

   (by the way, 8000 is about the size of the full dataset).
   The fold number should be a divisor of the number of the affiliations used.

   The best feature set and parameters are hard-coded in the script.
   But you can make experiments by changing the default parameters::

    ./cross_validate.sh training_data_size folds_number unique_name neighbor_feature_range rare_threshold 'features_list'

   for example::

    ./cross_validate.sh 100 4 1 2 '["Word", "Rare"]'

#. You may also want to use the scripts in order to train a model, which
   will be later deserialized and used in CERMINE. 
   We export the training data with
   the use of a Java class, namely 
   *pl.edu.icm.cermine.metadata.affiliations.tools.AffiliationTrainingDataExporter*.
   To export the data, call::
   
    ./train_all_java.sh

   This will use 8000 affiliations from *data/affs-real-like.xml* to train
   the ACRF.

#. (Optionally) you may want to train the ACRF so that it can tag authors.
   In order to do so, use::
  
    ./train_all_java_author.sh

   This will use 2000 affiliations from *data/affs-auth.xml*.

#.  We wanted to make sure that the Python and Java code
   tokenize affiliations and export features in the same way.
   You can check it by preparing a *javatests* directory with some data to export
   and calling::

    ./test_java_txt.sh
    diff javatests/features-*
    diff javatests/words-*


CRF testing tools
-----------------

#. If you want to choose a sample from a file with raw affiliation strings,
   use the *split_file.py* script. The script is also able to choose lines
   with ids that are not present in a given file. This is useful if you want
   to choose a subset of a large dataset such that it has an empty intersection
   with the training set.
   
#. The *hand_tags_to_xml.py* is useful for fast manual affiliation tagging.
   First, you have to prepare a text file with strings tagged like that::

    unnecessary head < institution part $ address part $ country part > unnecessary tail

   for example::
    
    Universidade Estadual de Ponta Grossa (UEPG),$ Ponta Grossa (PR),$ Brasil
    Jan Richarz< Department of Computer Science TU Dortmund,$$ Germany

   This script assumes that there are at most three affiliation parts and
   that they are in the order: *INST, ADDR, COUN*. Affiliation strings
   which do not follow this pattern have to be handled separately.

#. The script *test_hand.sh* is a slight modification of *train.sh*,
   which is more suitable for evaluating the ACRF on the preapared test data in
   a specific file.

#. Our testing results may be found in the *docs/result_*.txt* files.

#. The file *docs/sample_comp2.txt* contains a report from manual
   evaluation of a 100 sample from our training data.
