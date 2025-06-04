#!/bin/bash
# - SW - 27/05/2021 18:58 -
# Open the .iso in VLC, and build the Handbrake command interactively

if [ -z "$1" ]; then
    echo "Error: Please give input .iso path"
    exit 1
elif [ ! -f "$1" ] && [ ! -d "$1" ]; then
    echo "Error: Input '$1' not a valid file or directory"
    exit 1
fi
if [ ! -z "$2" ]; then
    OUTNAME="$2"
else
    OUTNAME=""
fi

ISO="$1"
ISO=$(echo $ISO | sed 's:/*$::')
LOG="${ISO}.log"
CMDFI="handbrake-jobs.sh"
OUTDIR="film"
MEDIA_DIR="/mnt/vulcan_a/data/media"

OUTDIR=$(echo $OUTDIR | sed 's:/*$::')
MEDIA_DIR=$(echo $MEDIA_DIR | sed 's:/*$::')

if [ ! -f "$CMDFI" ]; then
    echo "Output file '$CMDFI' not found. Creating..."
    echo '#!/bin/bash' > "$CMDFI"
    echo '' >> "$CMDFI"
    echo "MEDIA_DIR='$MEDIA_DIR'" >> "$CMDFI"
    echo '' >> "$CMDFI"
    chmod +x "$CMDFI"
fi

echo "Performing Handbrake scan..."
echo "--"
HandBrakeCLI --min-duration 60 -i "$ISO" -t 0
echo "--"
read -r -p 'Open file in VLC? ([Y]/n): ' response
case "$response" in
    [nN][oO]|[nN])
        echo "Skipping VLC"
        ;;
    *)
        echo "Opening file in VLC..."
        echo "--"
        vlc "$ISO"
        ;;
esac

sleep 2s
echo "--"

# Querying user for details
read -p "Output directory (inside '$MEDIA_DIR') [$OUTDIR]: " response
if [[ ! -z "$response" ]]; then
    OUTDIR="$response"
    OUTDIR=$(echo $OUTDIR | sed 's:/*$::')
    if [ ! -d "$MEDIA_DIR/$OUTDIR" ]; then
        echo "Directory '$OUTDIR' not found"
        exit 1
    fi
fi
echo "Output name -> 'Movie Title (YYYY)' without quotes, e.g. Output name: Jurassic Park (1993)"
while [ -z "$OUTNAME" ]; do
    read -p "Output name: " OUTNAME
done
echo "Choose from quality presets:"
echo "    1 - SuperHQ 1080"
echo "    2 - HQ 1080"
echo "    3 - Fast 1080"
read -r -p 'Quality preset [1]: ' response
if [ -z "$response" ]; then
    response=1
fi
case "$response" in
    1)
        PRESET="Super HQ 1080p30 Surround"
        SUFFIX="-superhq"
        ;;
    2)
        PRESET="HQ 1080p30 Surround"
        SUFFIX="-hq"
        ;;
    3)
        PRESET="Fast 1080p30"
        SUFFIX="-fast"
        ;;
    *)
        ;;
esac
read -r -p 'Title [1]: ' TITLE
if [ -z "$TITLE" ]; then
    TITLE=1
fi
read -r -p 'Audio Lang [eng]: ' LANG
if [ -z "$LANG" ]; then
    LANG=eng
fi
read -r -p 'Soft-subs English? ([Y]/n): ' response
case "$response" in
    [nN][oO]|[nN])
        read -r -p 'Burn in English subs? ([Y]/n): ' response
        case "$response" in
            [nN][oO]|[nN])
                echo 'Enter sub string manually in format: --subtitle "1,3" --subtitle-burned="2" --crop 0:0:0:0'
                echo 'Enter sub string manually in format: --subtitle "1,3" --subtitle-forced="2" --crop 0:0:0:0'
                read -p 'Sub-string: ' SUBS
                SUFFIX="$SUFFIX-sx.mkv"
                ;;
            *)
                SUBS='-N eng --subtitle-burned="native" --subtitle-default="none" --crop 0:0:0:0'
                SUFFIX="$SUFFIX-sb.mkv"
                ;;
        esac
        ;;
    *)
        SUBS='--subtitle-lang-list eng --subtitle-burned="none" --subtitle-default="none"'
        SUFFIX="$SUFFIX-ss.mkv"
        ;;
esac

echo "# '$ISO' - '$OUTNAME'" >> "$CMDFI"
echo "# Command generated at $(date)" >> "$CMDFI"
echo "# --------------------------------------------------" >> "$CMDFI"
echo "echo 'Transcoding \"$ISO\" -> \"$OUTNAME\"...'" >> "$CMDFI"
echo "echo '    less -RX +F \"$LOG\"'" >> "$CMDFI"
echo "HandBrakeCLI --min-duration 60 \\" >> "$CMDFI"
echo "-i \"$ISO\" \\" >> "$CMDFI"
echo "-o \""'${MEDIA_DIR}'"/$OUTDIR/$OUTNAME - "'${HOSTNAME}'"$SUFFIX\" \\" >> "$CMDFI"
echo "-t $TITLE \\" >> "$CMDFI"
echo "--audio-lang-list $LANG \\" >> "$CMDFI"
echo "--preset \"$PRESET\" \\" >> "$CMDFI"
echo "$SUBS &> $LOG" >> "$CMDFI"
echo "# --------------------------------------------------" >> "$CMDFI"
echo "" >> "$CMDFI"

