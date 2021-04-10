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

