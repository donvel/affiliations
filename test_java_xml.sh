features='["Word", "Number", "UpperCase", "AllUpperCase", "Address", "Country", "City", "State", "StateCode", "StopWord", "Separator", "NonAlphanum"]'

javatests=javatests

output=$javatests/features-expected-xml.txt

input=$javatests/affs-real-like.xml

neighbor=1

train_number=8000 # NEARLY ALL

test_number=0

python scripts/export.py --train $output \
    --input $input \
    --train_number $train_number \
    --test_number $test_number \
    --neighbor $neighbor \
    --xml_input 1 \
    --shuffle 0 \
    --mock_text_label 1 \
    "$features"
