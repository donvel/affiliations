python scripts/export.py --train_number=2 --test_number=1 --input=tests/test_export.xml \
    --hint=tests/test_hint.txt  --train=tests/test_train.txt --test=tests/test_test.txt \
    --rare=1 --neighbor=0 --split_alphanum=0 \
    '["Word", "UpperCase", "AllUpperCase", "Number", "AlphaNum", "Punct", \
    "WeirdLetter", "Freq", "Rare", "Length", "StopWord", "Country", "Address", \
    "Institution"]'


python scripts/export.py --train_number=2 --test_number=1 --input=tests/test_export.xml \
    --hint=tests/test_hint2.txt  --train=tests/test_train2.txt --test=tests/test_test2.txt \
    --neighbor=2 --split_alphanum=1 \
    '["Word"]'
