CERMINE=/home/bartek/Projects/CERMINE

GRMM=grmm

suffix=all_java

real=data/affs-real-like.xml

mock_test=data/affs-real-like-small.xml

crftrain=crfdata/train_$suffix.txt

acrf_prefix=crfdata/acrf_output_$suffix

acrf_suffix=Testing.txt

output=$acrf_prefix$acrf_suffix

err=crfdata/err_$suffix.xml

log_stdout=logs/stdout_$suffix.txt

log_err=logs/err_$suffix.txt

evaluator="new ACRFTrainer.LogEvaluator(\"$acrf_prefix\")"

model=crfdata/tmpls_chain.txt

nei_thr=1

java_jar=$CERMINE/cermine-impl/target/cermine-impl-1.3-SNAPSHOT-jar-with-dependencies.jar

java_class=pl.edu.icm.cermine.metadata.affiliations.tools.AffiliationTrainingDataExporter

java -cp $java_jar $java_class \
    --input $real \
    --output $crftrain \
    --neighbor $nei_thr

#python scripts/export.py \
#    --hint $hint \
#    --train $crftrain --test $crftest \
#    --input $real \
#    --train_number $number --test_number $tst_number \
#    --neighbor $nei_thr --rare $rare_thr --split_alphanum 1 \
#    --mock_text_label 1 \
#    "$features"

java -Xmx2000M \
    -cp $GRMM/class:$GRMM/lib/mallet-deps.jar:$GRMM/lib/grmm-deps.jar \
    edu.umass.cs.mallet.grmm.learning.GenericAcrfTui \
    --training $crftrain \
    --testing $mock_test \
    --eval "$evaluator" \
    --model-file $model > $log_stdout 2> $log_err
