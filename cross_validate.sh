i=$1

real=data/affs-real-like.xml

train=data/cross-train$i.txt

tst=data/cross-tst$i.txt

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

number=10

python scripts/split_data.py --number $number --cross 1 --part $i --input $real --test $tst --train $train --parts 5

python scripts/export.py \
    --train $crftrain --test $crftest \
    --input $train --input_test $tst \
    --train_number $((4*$number)) --test_number $number \
    --neighbor 1 --rare 0 --split_alphanum 1 \
    '["Word", "Number", "UpperCase"]'

java -Xmx2000M \
    -cp $GRMM/class:$GRMM/lib/mallet-deps.jar:$GRMM/lib/grmm-deps.jar \
    edu.umass.cs.mallet.grmm.learning.GenericAcrfTui \
    --training $crftrain \
    --testing $crftest \
    --eval "$evaluator" \
    --model-file $model > $log_stdout 2> $log_err

python scripts/count_score.py --input_file $output > $score 2> $scorelog
