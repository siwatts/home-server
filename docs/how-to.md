# How To

## About

How-to guide for some common generic tasks

## Partitioning and Formatting Drives

- Plug in USB HDD
- Identify devices / labels
    - `lsblk`
    - `fdisk -l`
- Re-partition a drive
    - Unmount if necessary with `umount`
    - `sudo fdisk /dev/sdX`
    - `d` to delete any existing partitions
    - `n` to create as many new as desired
    - `w` to write to disk
    - Can remove any ntfs signature if prompted, this is for Windows. Irrelevant
      if formatting as ext4
- Format partition 1 as ext4
    - `sudo mkfs.ext4 /dev/sdX1`
- Format partition 1 as FAT32 (useful for USB pen-drives for Windows/Linux use)
    - `sudo mkfs.vfat -F 32 /dev/sdX1`
- Mount ext4 partition
    - `sudo mkdir /mnt/mountpoint`
    - `sudo chown USER /mnt/mountpoint`, optional
    - `sudo mount /dev/sdc1 /mnt/mountpoint`
- Mount ext4 automatically on boot in `/etc/fstab`
    - `blkid`, to get UUID of drive
    - `/dev/disk/by-uuid/072d6... /mnt/mountpoint ext4 rw,user,exec 0 0`

## Plex Media Server

- Manage service
    - `sudo systemctl start plexmediaserver`
    - `sudo systemctl stop plexmediaserver`
    - `sudo systemctl status plexmediaserver`
    - `sudo systemctl disable plexmediaserver`
        - This prevents it from auto-starting on bootup
        - Still has to be stopped manually (do that first)
- Uninstall (for content and server migration)
    - `sudo apt remove --purge plexmediaserver`
- It is possible to migrate but this will physically move the actual plex server
  setup including IDs and servername etc. If re-installing on same machine
  because of OS re-install consider this

### Add Plug-in

- `/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Plug-ins`
- `.bundle` here
- Restart Plex server

## Rip DVDs

- Instructions followed for Ubuntu server 20.04 (orion, rigel)
- [Install libdvdcss](https://help.ubuntu.com/community/RestrictedFormats/PlayingDVDs)
    - `sudo apt install libdvd-pkg && sudo dpkg-reconfigure libdvd-pkg`
- Install handbrake
- Optional, add PPA to get latest
    - `sudo add-apt-repository ppa:stebbins/handbrake-releases`
    - `sudo apt update`
    - `sudo apt install handbrake-cli`
- Scan all titles on disk
    - `HandBrakeCLI -i /dev/cdrom -t 0`
- Rip using handbrake
    - `HandBrakeCLI -i /dev/cdrom -o name.mp4 --audio-lang-list eng`
- List DVD contents quickly
    - `sudo apt install lsdvd`
    - `lsdvd`
- `for i in `seq 4`; do HandBrakeCLI --input /dev/cdrom --title $i --output NameOfDisc_Title$i.mp4; done`
- Set region for DVD drive
    - `sudo apt install -y regionset`
    - `sudo regionset /dev/sr0`
    - Choose region 2 for UK / western Europe

### Dvdbackup

Sometimes discs are hard to backup with `dd` alone, or are corrupt and
unreadable at a certain point.

The utility `dvdbackup` can have more luck. Currently installed on `orion`

It can pad unreadable sections and handle read errors. For example

```
Error reading VTS_01_1.VOB at block 160
padding 352 blocks
```

Full instructions [here](https://wiki.archlinux.org/title/dvdbackup)

Summary:

```bash
# -M backup entire DVD structure, into a directory in location ~
dvdbackup -i /dev/dvd -o ~ -M
# Make .iso from resulting directory
mkisofs -dvd-video -udf -o ~/dvd.iso ~/movie_name
```

## Mounting Drives

### SSHFS

Fedora:
- `sudo dnf install -y fuse-sshfs`
- Recommended not to use root
- `mkdir -p ~/mnt/mountpoint`
- `sshfs [user@]host:[dir] mountpount [options]`
- E.g.
    - `mkdir -p ~/mnt/rigel_dvd-rips`
    - `sshfs lefler@rigel:/mnt/rigel_a1/data/media/dvd-rips ~/mnt/rigel_dvd-rips`

## Misc Server Admin

- Change `visudo` to vim
    - `sudo update-alternatives --config editor`

