input=data/improved-train.xml
output=data/real-like-train.xml

python scripts/remove_some_tags.py --input $input --output $output --address_ratio $1 --country_ratio $2

./train.sh 400 1 0 1 '["Word", "Punct", "Number", "UpperCase", "AllUpperCase", "Country", "Address", "Institution"]' test_ratio_$1_$2
