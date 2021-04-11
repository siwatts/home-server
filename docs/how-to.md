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

## Rip DVDs

- Instructions followed for Ubuntu server 20.04 (orion)
- [Install libdvdcss](https://help.ubuntu.com/community/RestrictedFormats/PlayingDVDs)
    - `sudo apt install libdvd-pkg && sudo dpkg-reconfigure libdvd-pkg`
- Install handbrake
- Optional, add PPA to get latest
    - `sudo add-apt-repository ppa:stebbins/handbrake-releases`
    - `sudo apt-get update`
- `sudo apt install handbrake-cli`
- Scan all titles on disk
    - `HandBrakeCLI -i /dev/cdrom -t 0`
- Rip using handbrake
    - `HandBrakeCLI -i /dev/cdrom -o name.mp4 --audio-lang-list eng`
- List DVD contents quickly
    - `sudo apt install lsdvd`
    - `lsdvd`
- `for i in `seq 4`; do HandBrakeCLI --input /dev/cdrom --title $i --output NameOfDisc_Title$i.mp4; done`

