suffix=all

real=data/affs-real-like.xml

crftrain=crfdata/train$suffix.txt

crftest=crfdata/test$suffix.txt

acrf_prefix=crfdata/acrf_output_$suffix

acrf_suffix=Testing.txt

output=$acrf_prefix$acrf_suffix

score_file=logs/score_$suffix.txt

hint=crfdata/hint_$suffix.txt

err=crfdata/err_$suffix.xml

err_html=crfdata/err_$suffix.html

label=crfdata/label_$suffix.xml

label_html=crfdata/label_$suffix.html

log_stdout=logs/stdout_$suffix.txt

log_err=logs/err_$suffix.txt

evaluator="new ACRFTrainer.LogEvaluator(\"$acrf_prefix\")"

model=crfdata/tmpls_chain.txt

GRMM=grmm

number=8000

tst_number=267

nei_thr=1

rare_thr=0

features='["Word", "Number", "UpperCase", "AllUpperCase", "Address", "Country", "City", "State", "StateCode", "StopWordMulti", "Punct", "WeirdLetter"]'

python scripts/export.py \
    --hint $hint \
    --train $crftrain --test $crftest \
    --input $real \
    --train_number $number --test_number $tst_number \
    --neighbor $nei_thr --rare $rare_thr --split_alphanum 1 \
    "$features"


java -Xmx2000M \
    -cp $GRMM/class:$GRMM/lib/mallet-deps.jar:$GRMM/lib/grmm-deps.jar \
    edu.umass.cs.mallet.grmm.learning.GenericAcrfTui \
    --training $crftrain \
    --testing $crftest \
    --eval "$evaluator" \
    --model-file $model > $log_stdout 2> $log_err

python scripts/count_score.py --error_file $err --label_file $label \
    --hint_file $hint --input_file $acrf_out --full_output 1 | tee $score_file
python scripts/make_readable.py --xml $err --html $err_html 
python scripts/make_readable.py --xml $label --html $label_html
