score=logs/cross-score

for i in 1 2 3 4 5
do
    ./cross_part.sh $i $1 &
done

wait

python scripts/aggregate_score.py $score?.txt | tee logs/aggr-score.txt

