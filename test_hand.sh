GRMM=grmm

affs=data/real-like-train.xml

affs_test=$1

model=crfdata/tmpls_chain.txt

test_number=92


train=crfdata/default-train_$2.txt

tst=crfdata/default-test_$2.txt

err=crfdata/default-err_$2.xml

hint=crfdata/default-hint_$2.txt

err_html=crfdata/default-err_$2.html

label=crfdata/default-label_$2.xml

label_html=crfdata/default-label_$2.html

log_stdout=logs/stdout_$2.txt

log_err=logs/err_$2.txt

score_file=logs/score_$2.txt

acrf_prefix=crfdata/acrf_output_$2_

acrf_suffix=Testing.txt

acrf_out=$acrf_prefix$acrf_suffix

evaluator="new ACRFTrainer.LogEvaluator(\"$acrf_prefix\")"

def_features='["Word", "Number", "UpperCase", "AllUpperCase", "Address", "Country", "City", "State", "StateCode", "StopWord", "Separator", "NonAlphanum"]'
features=${4:-$def_features}

python scripts/export.py --train $train --test $tst \
    --hint $hint \
    --input $affs --input_test $affs_test \
    --train_number $3 --test_number $test_number \
    --neighbor 1 --rare 0 --split_alphanum 1 \
    "$features"

java -Xmx2000M \
    -cp $GRMM/class:$GRMM/lib/mallet-deps.jar:$GRMM/lib/grmm-deps.jar \
    edu.umass.cs.mallet.grmm.learning.GenericAcrfTui \
    --training $train \
    --testing $tst \
    --eval "$evaluator" \
    --model-file $model > $log_stdout 2> $log_err

python scripts/count_score.py --error_file $err --label_file $label \
    --hint_file $hint --input_file $acrf_out --full_output 1 | tee $score_file
python scripts/make_readable.py --xml $err --html $err_html 
python scripts/make_readable.py --xml $label --html $label_html

#firefox $err_html &
