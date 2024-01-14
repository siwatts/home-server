# Docker Installation

## About

Installing onto `rigel`, 23/10/2021

Documenting which install method was used, and copying uninstall instructions at
time of install

If installing onto newer system, use latest instructions. This is provided for
reference for future uninstallation if required

## Docker Engine

https://docs.docker.com/engine/install/ubuntu/

Using apt repository method

Verified with
```bash
sudo docker run hello-world
```

Not following any of the optional post install steps (like `docker` user
creation - use `sudo`)

Should already be running as an enabled service. If not enable them. To disable
in future:
```bash
sudo systemctl stop docker.service; sudo systemctl disable docker.service
sudo systemctl stop containerd.service; sudo systemctl disable containerd.service
```

### Uninstall

Uninstall the Docker Engine, CLI, and Containerd packages:
```bash
sudo apt-get purge docker-ce docker-ce-cli containerd.io
```

Images, containers, volumes, or customized configuration files on your host are not automatically removed. To delete all images, containers, and volumes:
```bash
sudo rm -rf /var/lib/docker
sudo rm -rf /var/lib/containerd
```

## Docker Compose

Installing via Linux script method

Verify with `docker-compose --version`

### Uninstall

To uninstall Docker Compose if you installed using curl:

```bash
sudo rm /usr/local/bin/docker-compose
```

