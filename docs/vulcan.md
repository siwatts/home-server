# About

Replacement server, hostname: vulcan

This machine is a Dell Precision T3620

# Installation

- On date 28/08/2023
- RHEL 9.2 installed and registered, headless server
- Activate `sudo systemctl enable --now cockpit.socket` service
- Check ssh running
- Import git repo and keys, generate and add ssh key for vulcan
- Disabled ssh password login

## Programs

```bash
sudo dnf install vim tmux git
```

## RPM Fusion

- EPEL first
- RPM Fusion

# Storage

- 2x 4TB Seagate Ironwolf drives

# Import Data

## Rigel:

- Create `ro` NFS export from rigel, to allow for import of data to new primary
  data store
```
/mnt/rigel_a1 192.168.0.*(ro,sync,no_root_squash,no_subtree_check)
```
- Reload NFS exports with `sudo exportfs -ra`

## Vulcan:

- Add to `/etc/fstab` on Vulcan
```
# Readonly Rigel filesystem, to import to new primary data store
192.168.0.21:/mnt/rigel_a1 /mnt/rigel_a1 nfs ro,defaults 0 0
```
- Install NFS client, and mount
```
sudo dnf install -y nfs-utils
sudo mount -a
```

## mdadm Filesystem

**Note: This was undone**

- Creation of RAID0 filesystem on Vulcan
    - RAID0 means no redundancy but multiple drives into one extended partition
      by striping data across drives

Guide: https://www.digitalocean.com/community/tutorials/how-to-create-raid-arrays-with-mdadm-on-ubuntu-22-04

https://access.redhat.com/solutions/7025175

```
lsblk -o NAME,SIZE,FSTYPE,TYPE,MOUNTPOINT
sudo mdadm --create --verbose /dev/md0 --level=0 --raid-devices=2 /dev/sda /dev/sdb
cat /proc/mdstat
sudo mkdir /mnt/vulcan_int
lsblk
df -h
sudo mkfs.xfs /dev/md0
sudo mount /dev/md0 /mnt/vulcan_int
sudo chown lefler -R /mnt/vulcan_int
sudo mdadm --detail --scan | sudo tee -a /etc/mdadm.conf
# Test restarting after making test file on /mnt/vulcan_int
sudo umount /mnt/vulcan_int
sudo mdadm -S /dev/md0
sudo mdadm -As
```

`/etc/fstab`
```
# Internal storage RAID0
/dev/md0 /mnt/vulcan_int xfs defaults 0 2
```

- Was not able to run the update initramfs step. Is this required for mount to
  work on reboot? Trying before data sync...

- Make script to import data in `~/bin`
    - `rsync --dry-run -a --partial --inplace /mnt/rigel_a1/. /mnt/vulcan_int`

## Undo mdadm raid0 and make xfs drives

- Kept getting persistent failure of service, mdadm service `mdmonitor`
    - Failed to start
    - `DeviceDisappeared event detected on md device /dev/md/md0`
- Instructions from https://bobcares.com/blog/removal-of-mdadm-raid-devices/

Destroy mdadm, no packages installed of note
```
sudo -i
umount /dev/md0
cat /proc/mdstat
mdadm --stop /dev/md0
mdadm --remove /dev/md0
# error opening /dev/md0: No such file or directory
# This message can be expected according to guide
mdadm --zero-superblock /dev/sdb /dev/sdc
# lsblk and cat /proc/mdstat confirm no RAID devices running
# More steps from comments
rm /etc/mdadm.conf
# Remove /etc/fstab contents
# /dev/md0 /mnt/vulcan_int xfs defaults 0 2
```

# Create xfs filesystems

- Drives of interest, `/dev/sda`, `/dev/sdb`
    - Warning: Drive allocation moves around, since reboot and mdadm work above
      they have shifted. Use blkid

```
sudo -i
lsblk
rmdir /mnt/vulcan_int
mkdir /mnt/vulcan_a /mnt/vulcan_b
chown lefler:lefler /mnt/vulcan*
# fdisk could also be used?
# We will just use the entire drive though
mkfs.xfs /dev/sda
mkfs.xfs /dev/sdb
# Add to /etc/fstab using blkid output
systemctl daemon-reload
mount -a
sudo chown lefler:lefler /mnt/vulcan_*
# Initial big sync
bin/import-rigel-data.sh 2>&1 | tee sync-log.txt && sync && sudo shutdown 5
```

# NFS Server

- Steps taken as root

```
dnf install nfs-utils
systemctl status rpcbind
# enable --now rpcbind if not running
systemctl enable --now nfs-server
```

- Make blank `/etc/exports` file
- Fill with content

`/etc/exports`:
```
# File created manually on 05/09/2023 20:42

# Readonly test for everything on internal network
/mnt/vulcan_int 192.168.0.*(ro,sync,no_root_squash,no_subtree_check)
```

Reload NFS and try to mount and examine contents on intrepid

```
# Vulcan:
sudo exportfs -ra
sudo systemctl restart nfs-server
# Intrepid
sudo mkdir /mnt/vulcan_int
sudo mount 192.168.0.14:/mnt/vulcan_int /mnt/vulcan_int
```

Try firewall troubleshooting:

```
firewall-cmd --permanent --add-service nfs
firewall-cmd --reload
systemctl restart nfs-server
```

Found issue. `*` not valid in IP addresses anymore. Only in domain names or
entire IP. Must use bit range like `/24` instead

```
/mnt/vulcan_int 192.168.0.0/24(ro,sync,no_root_squash,no_subtree_check)
```
```
exportfs -ra
```

Now mounts on intrepid correctly

# Other TODO

- Register with Red Hat Insights? What does it do
- See if this machine is registered on Red Hat portal
- Set up system to host VMs
    - Plus bridged networking for VMs
- SMART test disks first

