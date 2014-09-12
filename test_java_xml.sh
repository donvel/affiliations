features='["Word", "Number", "UpperCase", "AllUpperCase", "AllLowerCase", "Rare", "Country", "Institution", "Address"]'

javatests=javatests

output=$javatests/features-expected-xml.txt

words=$javatests/words-expected-xml.txt

input=$javatests/affs-real-like.xml

neighbor=1

rare_thr=25

train_number=8267 # ALL

test_number=0

python scripts/export.py --train $output \
    --input $input \
    --common_words $words \
    --train_number $train_number \
    --test_number $test_number \
    --neighbor $neighbor \
    --rare $rare_thr \
    --xml_input 1 \
    --shuffle 0 \
    --mock_text_label 1 \
    "$features"
