score=logs/cross-score

python scripts/aggregate_score.py $score?.txt | tee logs/aggr-score.txt
