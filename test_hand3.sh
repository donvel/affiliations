GRMM=grmm

#affs=data/real-like-train.xml

affs_test=$1

affs=$2

model=crfdata/tmpls_chain.txt

test_number=$3


train=crfdata/default-train_$4.txt

tst=crfdata/default-test_$4.txt

err=crfdata/default-err_$4.xml

hint=crfdata/default-hint_$4.txt

err_html=crfdata/default-err_$4.html

label=crfdata/default-label_$4.xml

label_html=crfdata/default-label_$4.html

log_stdout=logs/stdout_$4.txt

log_err=logs/err_$4.txt

score_file=logs/score_$4.txt

acrf_prefix=crfdata/acrf_output_$4_

acrf_suffix=Testing.txt

acrf_out=$acrf_prefix$acrf_suffix

evaluator="new ACRFTrainer.LogEvaluator(\"$acrf_prefix\")"

def_train_number=1000
train_number=${5:-$def_train_number}

def_nei_thr=1
nei_thr=${6:-$def_nei_thr}

def_rare_thr=25
rare_thr=${7:-$def_rare_thr}

def_features='["Word", "Number", "AllUpperCase", "UpperCase", "AllLowerCase", "Country", "Institution", "Address", "Rare"]'
features=${8:-$def_features}


python scripts/export.py --train $train --test $tst \
    --hint $hint \
    --input $affs --input_test $affs_test \
    --train_number $train_number --test_number $test_number \
    --neighbor 1 --rare 16 --split_alphanum 1 \
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
