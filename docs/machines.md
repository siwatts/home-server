# Machines

## About

List of all hardware and physical machines, and their name / role

## Power Usage

Measured some typical power usage stats with plugin wall power meters

| Machine | Idle | Desktop | Plex stream | Transcoding | CPU Stress Test |
|---------|------|---------|-------------|-------------|-----------------|
| Rigel | 14.0 W | - | 15.2 W | 52.1 W | 41-42 W |
| Intrepid | | 34-40 W | |  | 107 W |
| Orion | | | | 64 W | |

CPU stress test:

- Install `stress` package
- `sudo stress --cpu 8 --timeout 20`
    - For an 8 thread system

