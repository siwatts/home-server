#!/bin/bash

echo "This will scan discs and build the commands for tv-ripper.py v1.4"
echo "  Usage: ./tv-ripper-helper.sh COMMAND_OUTPUT_FILE [SEASON NUM] [SEASON NAME] [INPUT_DIR] [OUTPUT_DIR]"
echo "  Warning: COMMAND_OUTPUT_FILE must be an absolute path"
echo

COMMAND_OUTPUT_FILE="$1"
if [[ -z "$COMMAND_OUTPUT_FILE" ]]; then
    echo "ERROR: No specified output target"
    exit 1
fi
echo "################################################################################" >> $COMMAND_OUTPUT_FILE
echo "# tv-ripper-helper.sh session: $(date)" >> $COMMAND_OUTPUT_FILE
echo "" >> $COMMAND_OUTPUT_FILE

# Take input

SE_NO="$2"
SE_NA="$3"
IN_DIR="$4"
OUT_DIR="$5"

echo "Season number - integer"
while [[ -z "$SE_NO" ]]; do
    read -p '  season = ' SE_NO
done
echo "Friendly season name - string"
while [[ -z "$SE_NA" ]]; do
    read -p '  season_name = ' SE_NA
done

echo "Input directory (for .iso) - string"
while [[ -z "$IN_DIR" ]]; do
    read -p '  input_directory = ' IN_DIR
done
IN_DIR=$(echo $IN_DIR | sed 's:/*$::')
echo "Output directory - string"
while [[ -z "$OUT_DIR" ]]; do
    read -p '  output_directory = ' OUT_DIR
done
OUT_DIR=$(echo $OUT_DIR | sed 's:/*$::')

# Want to do scans, so check
if [ ! -d "$IN_DIR" ]; then
    echo "Error: Input dir. not found"
    exit 1
fi

# Write it out
echo "    season = $SE_NO" >> $COMMAND_OUTPUT_FILE
echo "    season_name = '$SE_NA'" >> $COMMAND_OUTPUT_FILE
echo "    input_directory = '$IN_DIR'" >> $COMMAND_OUTPUT_FILE
echo "    output_directory = '$OUT_DIR'" >> $COMMAND_OUTPUT_FILE
echo "    series = DiscSeries(season_name, season, input_directory, output_directory)" >> $COMMAND_OUTPUT_FILE
echo "" >> $COMMAND_OUTPUT_FILE

pushd "$IN_DIR"
# Iterate over .iso
for f in *.iso; do
    echo "Working on disc: '$f'"
    echo "Disc number in the series - int"
    read -p '  disc_number = ' DISC_NO
    echo "Scanning... "
    echo "--"
    lsdvd "$f"
    echo "--"
    read -r -p 'Open disc in VLC? (y/[N]): ' response
    case "$response" in
        [yY][eE][sS]|[yY])
            echo "Opening file '$f' in vlc:"
            vlc "$f" &> /dev/null
            ;;
        *)
            ;;
    esac
    echo "Enter titles corresponding to these epsiodes - without square brackets e.g. 2,3,4,5"
    TI_LIST="["
    read -p "  title_override - <first in range> = [" FIRST_TI
    read -p "  title_override - <last in range?> [NONE] = [${FIRST_TI}-" LAST_TI
    if [[ -z "$LAST_TI" ]]; then
        # No range
        TI_LIST="${TI_LIST}${FIRST_TI},"
    else
        # Have a range of titles
        for i in `seq $FIRST_TI $LAST_TI`; do
            TI_LIST="${TI_LIST}${i},"
        done
    fi
    response="foo"
    while [[ ! -z $response ]]; do
        # Continue appending titles
        read -p "  title_override - <append> [NONE] = $TI_LIST" response
        TI_LIST="${TI_LIST}${response},"
    done
    TI_LIST="${TI_LIST%,*}]"
    echo "  title_override = $TI_LIST"

    # Write it out
    echo "    series.add_disc('$f', $DISC_NO, $TI_LIST)" >> $COMMAND_OUTPUT_FILE
    echo "--"
done
popd

echo "" >> $COMMAND_OUTPUT_FILE
echo "    series.rip_all()" >> $COMMAND_OUTPUT_FILE
echo "" >> $COMMAND_OUTPUT_FILE
echo "################################################################################" >> $COMMAND_OUTPUT_FILE
echo "" >> $COMMAND_OUTPUT_FILE
