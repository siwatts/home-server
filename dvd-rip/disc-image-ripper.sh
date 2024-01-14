#!/bin/bash
# - SW - 11/04/2021 21:31 -
# Iterate over several discs and rip them one be one to .iso with a suffix number
echo "----------------------"
echo "Disc image ripper v1.3"
echo "----------------------"
echo "Usage: ./disc-image-ripper.sh [NUM_DISCS] [OUTPUT_PREFIX]"
echo "----------------------"

NUM_DISCS=""
if [[ -z "$1" ]]; then
    while [[ -z "$NUM_DISCS" ]]; do
        read -p 'Enter number of discs in this series: ' NUM_DISCS
    done
else
    NUM_DISCS="$1"
fi
OUT_PREF=""
if [[ -z "$2" ]]; then
    while [[ -z "$OUT_PREF" ]]; do
        read -p 'Enter output prefix name/path: ' OUT_PREF
    done
else
    OUT_PREF="$2"
fi
OUT_PREF=$(echo $OUT_PREF | sed 's:/*$::')

echo "Settings:"
echo "- Iterating from discs 1-$NUM_DISCS"
echo "- Current working dir: '$(pwd)'"
echo "- Output prefix: '$OUT_PREF'"
echo "- Discs:"
for i in `seq 1 $NUM_DISCS`; do
    echo "  - Disc $i: '${OUT_PREF}${i}of${NUM_DISCS}.iso'"
done
echo "----------------------"

echo "Starting disc ingestion $(date)"

for i in `seq 1 $NUM_DISCS`; do
    out="${OUT_PREF}${i}of${NUM_DISCS}.iso"
    echo
    echo "This disc $i/$NUM_DISCS -> '$out'"
    echo "-- PLEASE INSERT DISC $i --"
    read -r -p 'Press ENTER to continue (s to skip) ([Y]/s): ' response
    case "$response" in
        [sS][kK][iI][pP]|[sS])
            echo
            echo "Skipping disc $i/$NUM_DISCS"
            ;;
        *)
            if [ -f "$out" ]; then
                echo "ERROR: File '$out' already exists. Aborting."
                exit 1
            fi
            echo
            echo "Pause 30s..."
            sleep 30s
            echo "Scanning disc $i/$NUM_DISCS..."
            sudo lsdvd || exit 1
            echo "Ripping disc $i/$NUM_DISCS..."
            sudo dd if=/dev/cdrom of="$out" status=progress && sync || exit 1
            sudo chown $USER:$USER "$out"
            echo "Done $i/$NUM_DISCS"
            ;;
    esac
done

echo
echo "Finished disc ingestion $(date)"
echo "Program complete"
echo
