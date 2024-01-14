# Pihole

## About

https://github.com/pi-hole/docker-pi-hole/

Installing pihole into docker container on `rigel`, 23/10/2021

Documented here not for instruction, but to reverse and uninstall in future if
required

## GitHub Installation Instructions

### Installing on Ubuntu

**THIS SECTION COPIED FROM README.MD**

Reverse the `resolv.conf` steps described below and softlink back original file
```
lrwxrwxrwx 1 root root 39 Feb  1  2021 /etc/resolv.conf -> ../run/systemd/resolve/stub-resolv.conf
```

### Raw

Modern releases of Ubuntu (17.10+) include [`systemd-resolved`](http://manpages.ubuntu.com/manpages/bionic/man8/systemd-resolved.service.8.html) which is configured by default to implement a caching DNS stub resolver. This will prevent pi-hole from listening on port 53.
The stub resolver should be disabled with: `sudo sed -r -i.orig 's/#?DNSStubListener=yes/DNSStubListener=no/g' /etc/systemd/resolved.conf`

This will not change the nameserver settings, which point to the stub resolver thus preventing DNS resolution. Change the `/etc/resolv.conf` symlink to point to `/run/systemd/resolve/resolv.conf`, which is automatically updated to follow the system's [`netplan`](https://netplan.io/):
`sudo sh -c 'rm /etc/resolv.conf && ln -s /run/systemd/resolve/resolv.conf /etc/resolv.conf'`
After making these changes, you should restart systemd-resolved using `systemctl restart systemd-resolved`

Once pi-hole is installed, you'll want to configure your clients to use it ([see here](https://discourse.pi-hole.net/t/how-do-i-configure-my-devices-to-use-pi-hole-as-their-dns-server/245)). If you used the symlink above, your docker host will either use whatever is served by DHCP, or whatever static setting you've configured. If you want to explicitly set your docker host's nameservers you can edit the netplan(s) found at `/etc/netplan`, then run `sudo netplan apply`.
Example netplan:
```yaml
network:
    ethernets:
        ens160:
            dhcp4: true
            dhcp4-overrides:
                use-dns: false
            nameservers:
                addresses: [127.0.0.1]
    version: 2
```

Note that it is also possible to disable `systemd-resolved` entirely. However, this can cause problems with name resolution in vpns ([see bug report](https://bugs.launchpad.net/network-manager/+bug/1624317)). It also disables the functionality of netplan since systemd-resolved is used as the default renderer ([see `man netplan`](http://manpages.ubuntu.com/manpages/bionic/man5/netplan.5.html#description)). If you choose to disable the service, you will need to manually set the nameservers, for example by creating a new `/etc/resolv.conf`.

Users of older Ubuntu releases (circa 17.04) will need to disable dnsmasq.

### Quick Start

**This section creates a docker-compose.yml file, and executes**

Doing this in `~/docker-stuff/pihole`

Using their file, but changing timezone `TZ` to `Europe/London`

Not sure if `# run `touch ./var-log/pihole.log` first unless you like errors`
refers to local path. Would be preferable. So creating dir:

```bash
mkdir ./var-log
touch ./var-log/pihole.log
```

Attempting to launch: `sudo docker-compose up -d`

## Use

Set DNS server to rigel IP. Should be automatically forwarded to container.

Verified that no new IP was added to Virgin Media router

### Samsung Q60T

Settings -> General -> Network -> Network Status -> IP Settings -> DNS setting

Previously: `Get automatically`
- `194.168.4.100`

Now: Manually set to Rigel IP

