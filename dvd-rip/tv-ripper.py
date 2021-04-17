#!/usr/bin/env python3
# coding=utf-8
# - SW - 11/04/2021 21:52 -
# Lay out a mapping of TV series to discs, then prompt interactively to read and convert them one by one
import subprocess
import re
import os.path
import datetime

class Disc:
    def __init__(self, disc_number, season_num, episode_list, starting_episode, output_dir, disc_is_avail=False, disc_location="/dev/dvd", title_indices_override=None):
        self.disc_number = disc_number
        self.season_num = season_num
        self.episode_list = episode_list
        self.required_title_count = len(episode_list)
        self.starting_episode = starting_episode
        self.output_dir = output_dir
        self.disc_is_avail = disc_is_avail
        self.disc_location = disc_location
        self.next_disc_starting_episode = starting_episode + sum(episode_list)
        self.title_indices_override = title_indices_override

        print("- disc {}: Eps {}-{} ({} required titles)".format(self.disc_number, self.starting_episode, self.next_disc_starting_episode-1, self.required_title_count))

    def scan(self):
        if not self.disc_is_avail:
            raise ValueError("Cannot scan disc {} yet, not available".format(self.disc_number))
        if self.disc_location is None:
            raise ValueError("Cannot scan disc {} yet, no location".format(self.disc_number))
        print("Disk {} is scanning...".format(self.disc_number))
        result = subprocess.run(['HandBrakeCLI', '--min-duration', '60', '-i', self.disc_location, '-t', '0'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print("Scan complete")
        result = result.stdout.decode('utf-8')
        self.disc_scan_result = result

        self.title_count = int(re.search('libhb: scan thread found (\d+) valid title', result).group(1))
        self.title_indices = list(map(int, re.findall('^\+ title (\d+):', result, re.MULTILINE)))

        if self.title_count != len(self.title_indices):
            raise ValueError("Did not parse disc scan result correctly. Need {} good titles but got {} title indices".format(self.title_count, len(self.title_indices)))

        if self.title_indices_override != None:
            # User has overridden the scan of all titles, make sure they're a subset
            newset = set(self.title_indices_override)
            oldset = set(self.title_indices)
            if not newset.issubset(oldset):
                raise ValueError("Invalid title override choice, not a subset of scan result valid titles")
            self.override_title_indices(self.title_indices_override)

        if self.required_title_count != self.title_count:
            print("Did not find the required number of good titles, found {}/{}".format(self.title_count, self.required_title_count))
            print("Override by calling Disc.override_title_indices(), and run this disc again")
            # TODO: Write out self.disc_scan_result to disk for use by user, or get them to fix the list interactively
        else:
            print("Found {}/{} good titles to rip".format(self.title_count, self.required_title_count))
            print("Ready to rip disc {}".format(self.disc_number))

    def override_title_indices(self, new_title_indices):
        self.title_indices = new_title_indices
        self.title_count = len(new_title_indices)
        print("Title indices overridden.")
        print("Are now {} titles to rip: {}".format(self.title_count, self.title_indices))

    def rip(self):
        if self.required_title_count != self.title_count:
            raise ValueError("Do not have the required {} number of good title indices, have {}".format(self.required_title_count, self.title_count))
        print("Ripping disc {}...".format(self.disc_number))

        ep = self.starting_episode
        for i in range(0, self.title_count):
            title = self.title_indices[i]
            eps = self.episode_list[i]
            ep_string = ""
            while eps > 0:
                ep_string = ep_string + "e" + f'{ep:02}'
                eps -= 1
                ep += 1
                if eps >= 1:
                    # Another to follow
                    ep_string = ep_string + "-"
            print("Title {} ({} of {}) - contains episodes '{}'...".format(title, i+1, self.title_count, ep_string))
            output_name = "s" + f'{self.season_num:02}' + ep_string + ep_trail_string + ".mp4"
            output_path = os.path.join(self.output_dir, output_name)
            if os.path.isfile(output_path):
                raise IOError("Output file '{}' already exists. Aborting".format(output_path))
            if hq:
                print("Executing command: 'HandBrakeCLI --min-duration 60 -i \"{}\" -o \"{}\" -t {} --audio-lang-list eng' --preset \"HQ 1080p30 Surround\"".format(self.disc_location, output_path, title))
                if global_dry_run:
                    print("-- DRY RUN --")
                else:
                    result = subprocess.run(['HandBrakeCLI', '--min-duration', '60', '-i', self.disc_location, '-o', output_path, '-t', str(title), '--audio-lang-list', 'eng', '--preset', 'HQ 1080p30 Surround'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            elif superhq:
                print("Executing command: 'HandBrakeCLI --min-duration 60 -i \"{}\" -o \"{}\" -t {} --audio-lang-list eng' --preset \"Super HQ 1080p30 Surround\"".format(self.disc_location, output_path, title))
                if global_dry_run:
                    print("-- DRY RUN --")
                else:
                    result = subprocess.run(['HandBrakeCLI', '--min-duration', '60', '-i', self.disc_location, '-o', output_path, '-t', str(title), '--audio-lang-list', 'eng', '--preset', 'Super HQ 1080p30 Surround'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            else:
                raise ValueError("Invalid program configuration at 'rip()'")


    def quickscan(self):
        print("Quick scan disc {}...".format(self.disc_number))
        result = subprocess.run(['lsdvd', self.disc_location])
        #result = subprocess.run(['lsdvd', self.disc_location], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)




class DiscsForIngestion:
    def __init__(self, list_of_discs, name):
        self.list_of_discs = list_of_discs
        self.name = name
        print("Created objects for '{}'".format(self.name))

    def ingest_all(self):
        print("Begin ingestion of '{}' at {}".format(self.name, datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")))

        for i in range(0+1,len(self.list_of_discs)+1):
            # +1 for 1-based index
            disc = self.list_of_discs[i-1]
            print("Ingesting disc {} ({}/{}) of '{}':".format(disc.disc_number, i, len(self.list_of_discs), self.name))
            if not disc.disc_is_avail:
                print()
                print("PLEASE INSERT DISC {} ({}/{})".format(disc.disc_number, i, len(self.list_of_discs)))
                input("Press ENTER when ready... ")
                print()
                # Now assume disc is changed and ready
                disc.disc_is_avail = True
            if quickscan:
                disc.quickscan()
            else:
                disc.scan()
                disc.rip()
            print("Finished ingesting disc {}".format(disc.disc_number))

        print("Finished ingestion of '{}' at {}".format(self.name, datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")))


if __name__ == "__main__":
    # execute only if run as a script

    print("---------------------")
    print("TV series Ripper v1.2")
    print("---------------------")
    global_dry_run = False
    hq = True
    superhq = False
    quickscan = False
    if (hq and superhq) or ((not hq) and (not superhq)):
        raise ValueError("Must choose either HQ or SuperHQ preset")
    if hq:
        ep_trail_string = ' - rigel-v1.2-hq-1080'
    elif superhq:
        ep_trail_string = ' - rigel-v1.2-superhq-1080'
    starttime = datetime.datetime.now()
    print("Program start: {}".format(starttime.strftime("%Y/%m/%d %H:%M:%S")))
    if global_dry_run:
        print("DRY-RUN ACTIVATED. Disc scans only (no rip or transcoding)")
    else:
        print("Running live. Disc ripping & transcoding enabled")
    print()

    ### SEASON 1 ###################################################################

    season = 1
    output_directory = "/mnt/rigel_a1/data/media/dvd-rips/tng/s01"
    discs = []
    discs.append(Disc(1, season, [2,1,1], 1, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s01/s01-disc-1of7.iso"))
    discs.append(Disc(2, season, [1,1,1,1], discs[-1].next_disc_starting_episode, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s01/s01-disc-2of7.iso"))
    discs.append(Disc(3, season, [1,1,1,1], discs[-1].next_disc_starting_episode, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s01/s01-disc-3of7.iso"))
    discs.append(Disc(4, season, [1,1,1,1], discs[-1].next_disc_starting_episode, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s01/s01-disc-4of7.iso"))
    discs.append(Disc(5, season, [1,1,1,1], discs[-1].next_disc_starting_episode, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s01/s01-disc-5of7.iso"))
    discs.append(Disc(6, season, [1,1,1,1], discs[-1].next_disc_starting_episode, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s01/s01-disc-6of7.iso"))
    discs.append(Disc(7, season, [1,1], discs[-1].next_disc_starting_episode, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s01/s01-disc-7of7.iso", [1,2]))

    season1 = DiscsForIngestion(discs, "TNG Season 1")

    ### SEASON 2 ###################################################################

    season = 2
    output_directory = "/mnt/rigel_a1/data/media/dvd-rips/tng/s02"
    discs = []
    discs.append(Disc(1, season, [1,1,1,1], 1, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s02/s02-disc-1of6.iso"))
    discs.append(Disc(2, season, [1,1,1,1], discs[-1].next_disc_starting_episode, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s02/s02-disc-2of6.iso"))
    discs.append(Disc(3, season, [1,1,1,1], discs[-1].next_disc_starting_episode, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s02/s02-disc-3of6.iso"))
    discs.append(Disc(4, season, [1,1,1,1], discs[-1].next_disc_starting_episode, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s02/s02-disc-4of6.iso"))
    discs.append(Disc(5, season, [1,1,1,1], discs[-1].next_disc_starting_episode, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s02/s02-disc-5of6.iso"))
    discs.append(Disc(6, season, [1,1], discs[-1].next_disc_starting_episode, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s02/s02-disc-6of6.iso", [1,2]))

    season2 = DiscsForIngestion(discs, "TNG Season 2")

    ### SEASON 3 ###################################################################

    season = 3
    output_directory = "/mnt/rigel_a1/data/media/dvd-rips/tng/s03"
    discs = []
    discs.append(Disc(1, season, [1,1,1,1], 1, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s03/s03-disc-1of7.iso"))
    discs.append(Disc(2, season, [1,1,1,1], discs[-1].next_disc_starting_episode, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s03/s03-disc-2of7.iso"))
    discs.append(Disc(3, season, [1,1,1,1], discs[-1].next_disc_starting_episode, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s03/s03-disc-3of7.iso"))
    discs.append(Disc(4, season, [1,1,1,1], discs[-1].next_disc_starting_episode, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s03/s03-disc-4of7.iso"))
    discs.append(Disc(5, season, [1,1,1,1], discs[-1].next_disc_starting_episode, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s03/s03-disc-5of7.iso"))
    discs.append(Disc(6, season, [1,1,1,1], discs[-1].next_disc_starting_episode, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s03/s03-disc-6of7.iso"))
    discs.append(Disc(7, season, [1,1], discs[-1].next_disc_starting_episode, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s03/s03-disc-7of7.iso", [1,2]))

    season3 = DiscsForIngestion(discs, "TNG Season 3")

    ### SEASON 5 ###################################################################

    season = 5
    output_directory = "/mnt/rigel_a1/data/media/dvd-rips/tng/s05"
    discs = []
    discs.append(Disc(1, season, [1,1,1,1], 1, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s05/s05-disc-1of7.iso"))
    discs.append(Disc(2, season, [1,1,1,1], discs[-1].next_disc_starting_episode, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s05/s05-disc-2of7.iso"))
    discs.append(Disc(3, season, [1,1,1,1], discs[-1].next_disc_starting_episode, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s05/s05-disc-3of7.iso"))
    discs.append(Disc(4, season, [1,1,1,1], discs[-1].next_disc_starting_episode, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s05/s05-disc-4of7.iso"))
    discs.append(Disc(5, season, [1,1,1,1], discs[-1].next_disc_starting_episode, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s05/s05-disc-5of7.iso"))
    discs.append(Disc(6, season, [1,1,1,1], discs[-1].next_disc_starting_episode, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s05/s05-disc-6of7.iso"))
    discs.append(Disc(7, season, [1,1], discs[-1].next_disc_starting_episode, output_directory, True, "/mnt/rigel_a1/data/media/dvd-rips/tng/s05/s05-disc-7of7.iso", [2,3]))

    season5 = DiscsForIngestion(discs, "TNG Season 5")

    print("---------------------")
    print("Begin ingestion")
    print("---------------------")

    season1.ingest_all()
    season2.ingest_all()
    season3.ingest_all()
    season5.ingest_all()

    print()
    print("Program complete")
    print("Stats:")

    endtime = datetime.datetime.now()
    duration = (endtime - starttime).total_seconds()
    print("  Program start: {}".format(starttime.strftime("%Y/%m/%d %H:%M:%S")))
    print("  Program end  : {}".format(endtime.strftime("%Y/%m/%d %H:%M:%S")))
    print("  Duration     : {:.0f}d {:.0f}h {:.0f}m {:.0f}s".format(duration // 86400, (duration // 3600) % 24, (duration // 60) % 60, duration % 60))
