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

Get exact size of a partition to duplicate it (for backup etc.)

- `sudo fdisk -l /dev/sdb1`
- `sudo blockdev --getsize64 /dev/sdb1`
- Fdisk:
    - `g` to create new GPT partition table (over certain size it is required)
    - `n`
    - Give sector count from above - 1, `+xxx`. If sector size matches, partition
      size matches. Else can give bytes
        - If drive you are copying reports 12 sectors, give +11.

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

## HandBrake Transcoding

### DVDs

### Conversion

For conversion of already existing media files, eg. raw DVD `.mpg`. No subtitle
or language considerations

```
HandBrakeCLI \
  -i input.mpg \
  -o output.mp4 \
  --preset "Super HQ 1080p30 Surround"
```

Preset options:
- `"Fast 1080p30"`
    - fast
- `"HQ 1080p30 Surround"`
    - hq
- `"Super HQ 1080p30 Surround"`
    - superhq

Can override framerate with `-r`, e.g. converting a 50fps file with duplicated
frames for regular viewing without incurring the 50->30 interpolation with `-r
25`
- Default is `--pfr` peak frame rate. Will decrease anything over `-r` value but
  leave anything under
- Can also specify `--cfr` and will force the fps chosen by `-r` everywhere

More untested preset options:
- `Vimeo YouTube HQ 1080p60`
- `Chromecast 2160p60 4K HEVC Surround`
    - h265
- `Chromecast 1080p60 Surround`
- `Chromecast 1080p30 Surround`
- `H.265 MKV 1080p30`
- `H.265 MKV 576p25`
- `H.264 MKV 2160p60`
- `H.264 MKV 1080p30`
- `H.264 MKV 576p25`
- `VP9 MKV 1080p30`
- `VP9 MKV 576p25`

## Downloads

Easily download web links, in a way that can resume on broken / partial download

```
# -c / --continue
wget -c web-url
# -i "file" / --input-file="file"
wget -i input-url-list -c
```

## Create NFS Server

Steps taken on rigel:

Need the IPs for this, e.g. of the client with `ifconfig -a`

- `sudo apt install nfs-kernel-server`
    - Was already installed
- `sudo vim /etc/exports`
    - `/mnt/rigel_a1/data/nfs-test 192.168.0.23(rw,sync,no_root_squash,no_subtree_check)`
    - You can use a range of IPs with `*`
- `sudo systemctl restart nfs-kernel-server` (actually appended `.service` via
  tab autocomplete
    - Actually this is not needed every time
    - `sudo exportfs -ra` to reload `/etc/exports` without restarting NFS
- On client:
    - `mkdir ~/mnt/rigel-nfs-test`
    - `sudo mount 192.168.0.21:/mnt/rigel_a1/data/nfs-test /home/simon/mnt/rigel-nfs-test`
    - Test success: Mounted as owned by my local account
- Test root mount in `/mnt/`
    - How does it appear from 2nd user
        - Owned by other user. Cannot wrte there
    - Is NFS v4 mapping uid 1000?
- Test root mount automatically by `/etc/fstab`
    - Options?
    - Intrepid:
        - `192.168.0.21:/mnt/rigel_a1 /mnt/rigel_a1 nfs rw,defaults 0 0`

## Virtual Machines

Steps taken on rigel:

- `sudo apt install -y qemu qemu-kvm libvirt-daemon libvirt-clients bridge-utils libvirt-daemon-system`
    - On client machine (those you wish to manage VMs with) `virt-manager`
- Connect `virt-manager` GUI via ssh and spawn remotely
- Check running with `sudo systemctl status libvirtd`

- Can use manual CLI method:
    - Theirs
        - `sudo virt-install --name ubuntu-guest --os-variant ubuntu20.04 --vcpus 2 --ram 2048 --location http://ftp.ubuntu.com/ubuntu/dists/focal/main/installer-amd64/ --network bridge=virbr0,model=virtio --graphics none --extra-args='console=ttyS0,115200n8 serial'`
    - Mine (failed)
        - `sudo virt-install --name ubuntu-test --os-variant ubuntu20.04 --vcpus 2 --ram 4096 --location /home/lefler/ubuntu-20.04.3-live-server-amd64.iso --network bridge=virbr0,model=virtio --graphics none --extra-args='console=ttyS0,115200n8 serial'`
    -  Mine (working)
        - `sudo virt-install --name ubuntu-test --os-variant ubuntu20.04 --vcpus 2 --ram 4096 --cdrom /home/lefler/ubuntu-20.04.3-live-server-amd64.iso --network bridge=virbr0,model=virtio --graphics none`
    - Remove
        - `virsh destroy ubuntu-test`
        - `virsh undefine ubuntu-test`
        - `virsh vol-delete --pool vg0 _domain-id_.img`

- Still failed
- `sudo apt install virtinst`
- Reboot
- Seemed to work

## Spin down drives when not in use

- Saves a small amount of power, but mostly noise
- Manually put drive into standby mode now
    - `sudo hdparm -y /dev/sdb`
    - Check current drive status with `sudo hdparm -C /dev/sdb`
- The timeout is set by `-S`
- See current timeout with
    - `sudo hdparm -I /dev/sdb | grep level`
- Timeout may be blocked by advanced power management setting of 128 or higher
    - See current: `sudo hdparm -B /dev/sdb`
    - Try 127 to enable standby spindown `sudo hdparm -B 127 /dev/sdb`
    - 26/03/2022 10:31:
        - Trying `sudo hdparm -B 127 /dev/sdb`
        - To revert, `sudo hdparm -B 128 /dev/sdb`

`man hdparm`, `-S`:
```
Values from 1 to 240 specify multiples of 5 seconds, yield‐ ing timeouts from 5
seconds to 20 minutes.  Values from 241 to 251 specify from 1 to 11 units of 30
minutes, yielding time‐ outs  from 30 minutes to 5.5 hours.  A value of 252
signifies a timeout of 21 minutes. A value of 253 sets a vendor-defined timeout
period between 8 and 12 hours, and the value 254 is reserved.  255 is
interpreted as 21 minutes  plus  15 seconds.
```
