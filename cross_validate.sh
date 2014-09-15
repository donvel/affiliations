score=logs/cross-score

number=$1

folds=$2

name=$3

def_nei_thr=1
nei_thr=${4:-$def_nei_thr}

def_rare_thr=25
rare_thr=${5:-$def_rare_thr}

def_features='["Word", "Number", "AllUpperCase", "UpperCase", "AllLowerCase", "Country", "Institution", "Address", "Rare"]'
features=${6:-$def_features}

rm -f $score*.txt

for i in $(seq 1 $folds)
do
    ./cross_part.sh $i $number $folds $nei_thr $rare_thr "$features" &
done

wait

python scripts/aggregate_score.py $score*.txt | tee logs/aggr-score-$name.txt

