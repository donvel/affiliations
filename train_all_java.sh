CERMINE=/home/bartek/Projects/CERMINE

GRMM=grmm

suffix=all_java

train=data/affs-all-train.xml

tst=data/affs-all-test.xml

crftrain=crfdata/train_$suffix.txt

crftst=crfdata/test_$suffix.txt

acrf_prefix=crfdata/acrf_output_$suffix

acrf_suffix=Testing.txt

output=$acrf_prefix$acrf_suffix

score_gile=/logs/score_$suffix.txt

log_stdout=logs/stdout_$suffix.txt

log_err=logs/err_$suffix.txt

evaluator="new ACRFTrainer.LogEvaluator(\"$acrf_prefix\")"

model=crfdata/tmpls_chain.txt

nei_thr=1

rare_thr=25

java_jar=$CERMINE/cermine-impl/target/cermine-impl-1.3-SNAPSHOT-jar-with-dependencies.jar

java_class=pl.edu.icm.cermine.metadata.affiliations.tools.AffiliationTrainingDataExporter

java -cp $java_jar $java_class \
    --input $train \
    --output $crftrain \
    --neighbor $nei_thr \
    --rare $rare_thr \
    --add_mock_text

java -cp $java_jar $java_class \
    --input $tst \
    --output $crftst \
    --neighbor $nei_thr

java -Xmx2000M \
    -cp $GRMM/class:$GRMM/lib/mallet-deps.jar:$GRMM/lib/grmm-deps.jar \
    edu.umass.cs.mallet.grmm.learning.GenericAcrfTui \
    --training $crftrain \
    --testing $crftst \
    --eval "$evaluator" \
    --model-file $model > $log_stdout 2> $log_err

python scripts/count_score.py --input_file $output --full_output 1 --use_hint 0 | tee $score_file
