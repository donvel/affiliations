Affiliation parsing CRF prototype
=================================

We use Python 2.7.5

Data preparation
----------------

#. We want to convert the tagged affiliations in `data/affs-parsed.txt` to valid XML.
   The script will print out invalid entries::
  
    scripts/affs_txt_to_rst.py
    
#. Then, we want to get rid off unnecessary tags (like `<italic>`)::

    scripts/strip_tags.py

#. Later, we want to tag the raw text in `data/affs-string.txt` by matching them
   with the tagged affiliations. The script will report how many lines got matched::

    scripts/match_text.py

#. We use a couple of rules to correct some common mistakes in tagging. For that
   we use `improve_data.py`. Some entries get rejected during this stage due to
   untagged content. They will be printed to stdout by the script.::

    scripts/improve_data.py

#. To browse the created dataset one may visualize it with::

    scripts/make_readable.py
    firefox data/affs-improved.html &


CRF training and evaluation
---------------------------

#. Choose the features you want to export and create the crf input files for
   training and testing. The only positional argument of the exporting script
   is a string representing a Python list. So you may invoke it like::

    scripts/export.py --train_number 1000 --test_number 5000 --neighbor 2 --rare 12 '["Word", "UpperCase", "AllUpperCase", "Number", "Punct", "Freq", "Rare", "Country"]'
