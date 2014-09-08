features='["Word", "Number", "UpperCase", "AllUpperCase", "Address", "Country", "City", "State", "StateCode", "StopWord", "Separator", "NonAlphanum"]'

javatests=javatests

output=$javatests/features-expected.txt

input=$javatests/affs.txt

neighbor=1

train_number=12203 # ALL

test_number=0

python scripts/export.py --train $output \
    --input $input \
    --train_number $train_number \
    --test_number $test_number \
    --neighbor $neighbor \
    --xml_input 0 \
    --shuffle 0 \
    "$features"
