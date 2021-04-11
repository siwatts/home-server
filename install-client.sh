#!/bin/bash
# - SW - 10/04/2021 22:57 -
# Quick install a new client to the home server setup

# List some locations
SSH_CONFIG_LO="$HOME/.ssh/config"
SSH_CONFIG_RE='ssh/config'
SSH_AUTHK_LO="$HOME/.ssh/authorized_keys"
SSH_AUTHK_RE='ssh/authorized_keys'
SSH_IDPUB_LO="$HOME/.ssh/id_rsa.pub"

# Quickly check we are in the right place
if [ ! -f "$SSH_AUTHK_RE" ]; then
    tput setaf 1; tput bold
    echo "ERROR: Cannot see file '$SSH_AUTHK_RE', please run script from root of repository"
    tput sgr0
    exit 0
fi

# Begin
if [ ! -f "$SSH_IDPUB_LO" ]; then
    echo "Found no SSH public key '$SSH_IDPUB_LO'"
    read -r -p "Call 'ssh-keygen' to generate one now? ([Y]/n): " response
    case "$response" in
        [nN][oO]|[nN])
            echo "Aborting"
            exit 0
            ;;
        *)
            ssh-keygen
            ;;
    esac
fi

if [ -f $SSH_IDPUB_LO ]; then
    echo "Found SSH public key '$SSH_IDPUB_LO'"
    echo "Appending to list of authorized keys..."
    cat "$SSH_IDPUB_LO" >> "$SSH_AUTHK_RE"
else
    tput setaf 1; tput bold
    echo "ERROR: Found no SSH key '$SSH_IDPUB_LO'"
    echo "Aborting"
    tput sgr0
    exit 0
fi

echo "Import global authorized_keys file? This will allow all other machines to SSH back to this local machine"
read -r -p 'Import authorized_keys? (y/[N]): ' response
case "$response" in
    [yY][eE][sS]|[yY])
        if [ -f "$SSH_AUTHK_LO" ]; then
            tput setaf 5
            echo "WARNING: Found existing '$SSH_AUTHK_LO' file, moving to '$SSH_AUTHK_LO.bak'"
            echo "         Please delete or merge these files"
            tput sgr0
            mv "$SSH_AUTHK_LO" "$SSH_AUTHK_LO.bak"
        fi
        echo "Soft-linking '$SSH_AUTHK_RE'..."
        ln -s "$(pwd)/$SSH_AUTHK_RE" "$SSH_AUTHK_LO"
        ;;
    *)
        ;;
esac

echo "Importing SSH hosts file '$SSH_CONFIG_RE'..."
if [ -f $SSH_CONFIG_LO ]; then
    tput setaf 5
    echo "WARNING: Found existing '$SSH_CONFIG_LO' file, moving to '$SSH_CONFIG_LO.bak'"
    echo "         Please delete or merge these files"
    tput sgr0
    mv "$SSH_CONFIG_LO" "$SSH_CONFIG_LO.bak"
fi
echo "Soft-linking SSH hosts file '$SSH_CONFIG_RE'..."
ln -s "$(pwd)/$SSH_CONFIG_RE" "$SSH_CONFIG_LO"

echo "Fixing some file permissions..."
chmod 600 "$SSH_AUTHK_LO"
chmod 664 "$SSH_CONFIG_LO"

if [ -f "$SSH_CONFIG_LO.bak" ]; then
    echo "Opening files for comparison in vimdiff : '$SSH_CONFIG_LO' -> '$SSH_CONFIG_LO.bak'..."
    echo "  '$SSH_CONFIG_LO.bak' will be deleted on successful exit code. Exit with ':cq' to avoid this."
    read -r -p "Compare files? (y/[N]): " response
    case "$response" in
        [yY][eE][sS]|[yY])
            vimdiff "$SSH_CONFIG_LO" "$SSH_CONFIG_LO.bak" && rm "$SSH_CONFIG_LO.bak"
            ;;
        *)
            ;;
    esac
fi

if [ -f "$SSH_AUTHK_LO.bak" ]; then
    echo "Opening files for comparison in vimdiff : '$SSH_AUTHK_LO' -> '$SSH_AUTHK_LO.bak'..."
    echo "  '$SSH_AUTHK_LO.bak' will be deleted on successful exit code. Exit with ':cq' to avoid this."
    read -r -p "Compare files? (y/[N]): " response
    case "$response" in
        [yY][eE][sS]|[yY])
            vimdiff "$SSH_AUTHK_LO" "$SSH_AUTHK_LO.bak" && rm "$SSH_AUTHK_LO.bak"
            ;;
        *)
            ;;
    esac
fi

echo ""
echo "Done"
exit 1
