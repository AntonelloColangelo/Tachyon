#!/bin/bash
## COMPARE TACHYON WITH STAR
# Checks that Tachyon gave the same results as STAR 2.7.11b, run on the same reads with the same index, options and threads.
# Use:   bash compare_with_star.sh STAR_OUTPUT_FOLDER TACHYON_OUTPUT_FOLDER
# Needs samtools. Both BAM files are read in full: on a few million read pairs it takes a minute or two.
# It applies the criterion used for every benchmark of Tachyon:
#   - alignment records, decoded to text and sorted (records at the same position can change order between runs, also with STAR)
#   - BAM header without the @PG and @CO lines, which hold the program name and the command
#   - SJ.out.tab and ReadsPerGene.out.tab, byte by byte
#   - Log.final.out without the lines with dates and speeds
# The last line says SAME AS STAR or DIFFERENT FROM STAR, with the files that differ. The exit code is 0, 1, or 2 if the check could not run.

STAR_OUT=$1
TACHYON_OUT=$2
set -o pipefail
export LC_ALL=C

## 1. TOOLS AND FOLDERS

if ! command -v samtools > /dev/null; then
    echo "STOP: samtools is missing. Install it, then run this script again."
    exit 2
fi
if [ ! -f "$STAR_OUT/Log.final.out" ] || [ ! -f "$TACHYON_OUT/Log.final.out" ]; then
    echo "STOP: give the two output folders, STAR first. Each must contain Log.final.out."
    echo "Use: bash compare_with_star.sh STAR_OUTPUT_FOLDER TACHYON_OUTPUT_FOLDER"
    exit 2
fi

## 2. ALIGNMENT RECORDS

# every alignment file the two programs wrote, whichever --outSAMtype produced it; a file from only one of them is a difference
DIFFERENT=""
COMPARED=""
for BAM in Aligned.sortedByCoord.out.bam Aligned.out.bam Aligned.out.sam; do
    [ -f "$STAR_OUT/$BAM" ] || [ -f "$TACHYON_OUT/$BAM" ] || continue
    if [ ! -f "$STAR_OUT/$BAM" ] || [ ! -f "$TACHYON_OUT/$BAM" ]; then
        DIFFERENT="$DIFFERENT $BAM(missing)"
        continue
    fi

    # header without @PG and @CO
    STAR_HEADER=$(samtools view -H "$STAR_OUT/$BAM" | grep -v -E "^@(PG|CO)" | md5sum) || { echo "STOP: cannot read $STAR_OUT/$BAM"; exit 2; }
    TACHYON_HEADER=$(samtools view -H "$TACHYON_OUT/$BAM" | grep -v -E "^@(PG|CO)" | md5sum) || { echo "STOP: cannot read $TACHYON_OUT/$BAM"; exit 2; }
    [ "$STAR_HEADER" = "$TACHYON_HEADER" ] || DIFFERENT="$DIFFERENT $BAM(header)"

    # every record, decoded and sorted as text
    STAR_RECORDS=$(samtools view "$STAR_OUT/$BAM" | sort -S 2G -T "${TMPDIR:-/tmp}" | md5sum) || { echo "STOP: cannot read $STAR_OUT/$BAM"; exit 2; }
    TACHYON_RECORDS=$(samtools view "$TACHYON_OUT/$BAM" | sort -S 2G -T "${TMPDIR:-/tmp}" | md5sum) || { echo "STOP: cannot read $TACHYON_OUT/$BAM"; exit 2; }
    [ "$STAR_RECORDS" = "$TACHYON_RECORDS" ] || DIFFERENT="$DIFFERENT $BAM(records)"

    STAR_COUNT=$(samtools view -c "$STAR_OUT/$BAM")
    TACHYON_COUNT=$(samtools view -c "$TACHYON_OUT/$BAM")
    echo "$BAM: $STAR_COUNT records from STAR, $TACHYON_COUNT from Tachyon"
    [ "$STAR_COUNT" -gt 0 ] && COMPARED="$COMPARED $BAM"
done
if [ -z "$COMPARED" ] && [ -z "$DIFFERENT" ]; then
    echo "STOP: no alignment records to compare (looked for Aligned.sortedByCoord.out.bam, Aligned.out.bam and Aligned.out.sam)."
    exit 2
fi

## 3. JUNCTIONS, GENE COUNTS AND STATISTICS

# a table written by only one of the two programs is a difference
for TABLE in SJ.out.tab ReadsPerGene.out.tab; do
    [ -f "$STAR_OUT/$TABLE" ] || [ -f "$TACHYON_OUT/$TABLE" ] || continue
    cmp -s "$STAR_OUT/$TABLE" "$TACHYON_OUT/$TABLE" || DIFFERENT="$DIFFERENT $TABLE"
    COMPARED="$COMPARED $TABLE"
done

# Log.final.out without the lines that change at every run
cmp -s <(grep -v -E "Started|Finished|speed" "$STAR_OUT/Log.final.out") \
       <(grep -v -E "Started|Finished|speed" "$TACHYON_OUT/Log.final.out") || DIFFERENT="$DIFFERENT Log.final.out"
COMPARED="$COMPARED Log.final.out"

## 4. RESULT

echo
if [ -z "$DIFFERENT" ]; then
    echo "Compared:$COMPARED"
    echo "SAME AS STAR"
    exit 0
fi
echo "DIFFERENT FROM STAR:$DIFFERENT"
echo "Check that both runs used the same reads, index, options and --runThreadN."
exit 1
