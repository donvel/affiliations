python scripts/export.py --train_number=2 --test_number=1 --input=tests/test_export.xml \
    --hint=tests/export_hint.txt  --train=tests/export_train.crf --test=tests/export_test.crf \
    --rare=1 --neighbor=0 --split_alphanum=0 \
    '["Word", "UpperCase", "AllUpperCase", "Number", "AlphaNum", "Punct", \
    "WeirdLetter", "Freq", "Rare", "Length", "StopWord", "Country", "Address", \
    "Institution", "City", "State", "StateCode"]'

python scripts/export.py --train_number=2 --test_number=1 --input=tests/test_export.xml \
    --hint=tests/export_hint2.txt  --train=tests/export_train2.crf --test=tests/export_test2.crf \
    --neighbor=2 --split_alphanum=1 \
    '["Word"]'
