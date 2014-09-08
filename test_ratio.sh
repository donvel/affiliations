name=test_ratio_$1_$2_$3
input=data/improved-train.xml
output=data/real-like-train_$name.xml

python scripts/remove_some_tags.py --input $input --output $output --address_ratio $1 --country_ratio $2 --ac_ratio $3

./train.sh 4000 2 0 1 '["Separator", "UpperCase", "AllUpperCase", "Number", "Address", "Country", "Word", "StopWord", "City", "State"]' $name &
