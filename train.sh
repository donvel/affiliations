GRMM=grmm
train=crfdata/default-train.txt
tst=crfdata/default-test.txt
affs=data/real-like-train.xml
affs_test=data/real-like-test.xml
model=crfdata/tmpls_chain.txt
err=crfdata/default-err.xml
err_html=crfdata/default-err.html
label=crfdata/default-label.xml
label_html=crfdata/default-label.html
test_number=3000
split_alphanum=1 

python scripts/export.py --train $train --test $tst \
    --input $affs --input_test $affs_test \
    --train_number $1 --test_number $test_number \
    --neighbor $2 --rare $3 --split_alphanum $split_alphanum \
    "$4"

java -Xmx2000M \
    -cp $GRMM/class:$GRMM/lib/mallet-deps.jar:$GRMM/lib/grmm-deps.jar \
    edu.umass.cs.mallet.grmm.learning.GenericAcrfTui \
    --training $train \
    --testing $tst \
    --model-file $model 2> logs/err_$1_$2_$3.txt

python scripts/count_score.py --error_file $err --label_file $label
python scripts/make_readable.py --xml $err --html $err_html 
python scripts/make_readable.py --xml $label --html $label_html

firefox $err_html &
