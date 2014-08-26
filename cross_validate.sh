score=logs/cross-score

number=$1

folds=$2

def_nei_thr=1
nei_thr=${3:-$def_nei_thr}

def_rare_thr=3
rare_thr=${4:-$def_rare_thr}

def_features='["Word", "Number", "UpperCase", "AllUpperCase", "Address", "Country", "City", "State", "StateCode", "StopWordMulti", "Punct", "WeirdLetter"]'
features=${5:-$def_features}

rm $score*.txt

for i in $(seq 1 $folds)
do
    ./cross_part.sh $i $number $folds $nei_thr $rare_thr "$features" &
done

wait

python scripts/aggregate_score.py $score*.txt | tee logs/aggr-score.txt

