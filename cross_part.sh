i=$1

real=data/affs-real-like.xml

train=data/cross-train$i.xml

tst=data/cross-tst$i.xml

crftrain=crfdata/cross-train$i.txt

crftest=crfdata/cross-test$i.txt

score=logs/cross-score$i.txt

scorelog=logs/part-score$i.txt

acrf_prefix=crfdata/acrf_output_$i

acrf_suffix=Testing.txt

output=$acrf_prefix$acrf_suffix

log_stdout=logs/cross_stdout_$i.txt

log_err=logs/cross_err_$i.txt

evaluator="new ACRFTrainer.LogEvaluator(\"$acrf_prefix\")"

model=crfdata/tmpls_chain.txt

GRMM=grmm

part_number=$(($2 / $3))

parts=$3

nei_thr=$4

rare_thr=$5

features=$6

python scripts/split_data.py --number $part_number --cross 1 --part $i --input $real --test $tst --train $train --parts $parts

python scripts/export.py \
    --train $crftrain --test $crftest \
    --input $train --input_test $tst \
    --train_number $((($parts - 1) * $part_number)) --test_number $part_number \
    --neighbor $nei_thr --rare $rare_thr --split_alphanum 1 \
    "$features"

echo --train_number $((($parts - 1) * $part_number)) --test_number $part_number --neighbor $nei_thr --rare $rare_thr --split_alphanum 1 "$features"


java -Xmx2000M \
    -cp $GRMM/class:$GRMM/lib/mallet-deps.jar:$GRMM/lib/grmm-deps.jar \
    edu.umass.cs.mallet.grmm.learning.GenericAcrfTui \
    --training $crftrain \
    --testing $crftest \
    --eval "$evaluator" \
    --model-file $model > $log_stdout 2> $log_err

python scripts/count_score.py --input_file $output > $score 2> $scorelog
