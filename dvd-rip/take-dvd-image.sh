#!/bin/bash
# - SW - 12/04/2021 00:46 -
# Take a simple .iso image of a DVD

sudo lsdvd /dev/cdrom
echo "--"

# Try to get disc title dynamically:
if [ -z "$1" ]; then
    echo "Attempting disc title auto-detect..."
    TITLE="$(sudo lsdvd /dev/cdrom | grep 'Disc Title:' | sed 's/Disc Title: //')"
    echo "Detected Disc Title: '$TITLE'"
    echo
    echo "Override output filename? Blank to accept default"
    read -p "  Output Filename [${TITLE}.iso]: " userinput
    if [[ -z "$userinput" ]]; then
        # Also catches whitespace
        OUTPUT="${TITLE}.iso"
    else
        OUTPUT="$userinput"
    fi
else
    echo "Using command line output param: '$1'"
    OUTPUT="$1"
fi

echo
echo "About to run following command:"
echo "  sudo dd if=/dev/cdrom of="$OUTPUT" status=progress && sync"
echo "  sudo chown ${USER}:${USER} ${OUTPUT}"

echo ""
read -r -p 'PRESS ENTER TO CONTINUE...' response

#sudo ls > /dev/null
echo "Begin @ $(date)"
sudo dd if=/dev/cdrom of="$OUTPUT" status=progress && sync
sudo chown ${USER}:${USER} "${OUTPUT}"

echo "Complete @ $(date)"

