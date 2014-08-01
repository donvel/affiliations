GRMM=grmm

affs=data/real-like-train.xml

affs_test=data/real-like-test.xml

model=crfdata/tmpls_chain.txt

test_number=4267


train=crfdata/default-train_$6.txt

tst=crfdata/default-test_$6.txt

err=crfdata/default-err_$6.xml

hint=crfdata/default-hint_$6.txt

err_html=crfdata/default-err_$6.html

label=crfdata/default-label_$6.xml

label_html=crfdata/default-label_$6.html

log_stdout=logs/stdout_$6.txt

log_err=logs/err_$6.txt

score_file=logs/score_$6.txt

acrf_prefix=crfdata/acrf_output_$6_

acrf_suffix=Testing.txt

acrf_out=$acrf_prefix$acrf_suffix

evaluator="new ACRFTrainer.LogEvaluator(\"$acrf_prefix\")"


python scripts/export.py --train $train --test $tst \
    --hint $hint \
    --input $affs --input_test $affs_test \
    --train_number $1 --test_number $test_number \
    --neighbor $2 --rare $3 --split_alphanum $4 \
    "$5"

java -Xmx2000M \
    -cp $GRMM/class:$GRMM/lib/mallet-deps.jar:$GRMM/lib/grmm-deps.jar \
    edu.umass.cs.mallet.grmm.learning.GenericAcrfTui \
    --training $train \
    --testing $tst \
    --eval "$evaluator" \
    --model-file $model > $log_stdout 2> $log_err

python scripts/count_score.py --error_file $err --label_file $label \
    --hint_file $hint --input_file $acrf_out | tee $score_file
python scripts/make_readable.py --xml $err --html $err_html 
python scripts/make_readable.py --xml $label --html $label_html

#firefox $err_html &
