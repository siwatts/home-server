#!/usr/bin/env python3
# coding=utf-8
# - SW - 11/04/2021 21:52 -
# Lay out a mapping of TV series to discs, then prompt interactively to read and convert them one by one
import subprocess
import re
import os.path
import datetime
import socket

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
                print("Executing command: 'HandBrakeCLI --min-duration 60 -i \"{}\" -o \"{}\" -t {} --audio-lang-list eng' --preset \"Fast 1080p30\"".format(self.disc_location, output_path, title))
                if global_dry_run:
                    print("-- DRY RUN --")
                else:
                    result = subprocess.run(['HandBrakeCLI', '--min-duration', '60', '-i', self.disc_location, '-o', output_path, '-t', str(title), '--audio-lang-list', 'eng', '--preset', 'Fast 1080p30'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


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

    def rip_all(self):
        print("Begin rip of '{}' at {}".format(self.name, datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")))

        for i in range(0+1,len(self.list_of_discs)+1):
            # +1 for 1-based index
            disc = self.list_of_discs[i-1]
            print("Ripping disc {} ({}/{}) of '{}':".format(disc.disc_number, i, len(self.list_of_discs), self.name))
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
                disc.rip()
            print("Finished ripping disc {}".format(disc.disc_number))

        print("Finished ripping of '{}' at {}".format(self.name, datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")))

class DiscSeries:
    # To be used to build DiscsForIngestion class, only when all discs are available (ie. scanned onto HDD as .iso)
    def __init__(self, friendly_name, season_no, input_directory, output_directory):
        # Param
        self.friendly_name = friendly_name
        self.input_directory = input_directory
        self.output_directory = output_directory
        self.season_no = season_no
        # Member
        self.disc_list = []
        self.discs_for_ingestion = None
        self.nextepisode = 1

    def add_disc(self, filename, disc_number, title_override, episode_list=None, first_ep_override=None):
        if (first_ep_override != None):
            first_ep = first_ep_override
        else:
            first_ep = self.nextepisode

        if episode_list == None:
            # Episode list not specified, assuming all episodes are 1 unit long
            # (no composite double episodes in one title)
            episode_list = [1] * len(title_override)

        input_filepath = os.path.join(self.input_directory, filename)
        thisdisc = Disc(disc_number, self.season_no, episode_list, first_ep, self.output_directory, True, input_filepath, title_override)
        if title_override != None:
            thisdisc.override_title_indices(title_override)
        self.disc_list.append(thisdisc)
        self.nextepisode = thisdisc.next_disc_starting_episode

    def rip_all(self):
        if self.discs_for_ingestion == None:
            self.discs_for_ingestion = DiscsForIngestion(self.disc_list, self.friendly_name)

        self.discs_for_ingestion.rip_all()

    def ingest_all(self):
        if self.discs_for_ingestion == None:
            self.discs_for_ingestion = DiscsForIngestion(self.disc_list, self.friendly_name)

        self.discs_for_ingestion.ingest_all()

if __name__ == "__main__":
    # execute only if run as a script

    this_prog_version = "v1.4"
    print("---------------------")
    print("TV series Ripper {}".format(this_prog_version))
    print("---------------------")
    global_dry_run = False
    hq = True
    superhq = False
    quickscan = False
    hostname = socket.gethostname()
    print("Hostname: {}".format(hostname))
    if (hq and superhq):
        raise ValueError("Must choose either HQ or SuperHQ preset")
    if hq:
        ep_trail_string = " - {}-{}-hq-1080".format(hostname, this_prog_version)
        print("Using preset: HQ 1080p30 Surround")
    elif superhq:
        ep_trail_string = " - {}-{}-superhq-1080".format(hostname, this_prog_version)
        print("Using preset: Super HQ 1080p30 Surround")
    else:
        ep_trail_string = " - {}-{}-fast-1080".format(hostname, this_prog_version)
        print("Using preset: Fast 1080p30")
    starttime = datetime.datetime.now()
    print("Program start: {}".format(starttime.strftime("%Y/%m/%d %H:%M:%S")))
    if global_dry_run:
        print("DRY-RUN ACTIVATED. Disc scans only (no rip or transcoding)")
    else:
        print("Running live. Disc ripping & transcoding enabled")
    print()

#################################################################################
## tv-ripper-helper.sh session: Tue 20 Apr 19:33:18 BST 2021
#
#    season = 5
#    season_name = 'Simpsons Season 5'
#    input_directory = ''
#    output_directory = '/home/simon/mnt/simpsons/Season 05'
#    series = DiscSeries(season_name, season, input_directory, output_directory)
#
#    series.add_disc('s05-disc-1of4.iso', 1, [2,3,4,5,6,])
#    series.add_disc('s05-disc-2of4.iso', 2, [2,3,4,5,6,7,])
#    series.add_disc('s05-disc-3of4.iso', 3, [2,3,4,5,6,7,])
#    series.add_disc('s05-disc-4of4.iso', 4, [2,3,4,5,6,])
#
#    series.rip_all()
#
#################################################################################
#
#################################################################################
## tv-ripper-helper.sh session: Tue 20 Apr 19:36:14 BST 2021
#
#    season = 6
#    season_name = 'Simpsons Season 6'
#    input_directory = ''
#    output_directory = '/home/simon/mnt/simpsons/Season 06'
#    series = DiscSeries(season_name, season, input_directory, output_directory)
#
#    series.add_disc('s06-disc-1of4.iso', 1, [2,3,4,5,6,7,8,])
#    series.add_disc('s06-disc-2of4.iso', 2, [2,3,4,5,6,7,8,])
#    series.add_disc('s06-disc-3of4.iso', 3, [2,3,4,5,6,7,8,])
#    series.add_disc('s06-disc-4of4.iso', 4, [2,3,4,5,])
#
#    series.rip_all()
#
#################################################################################

################################################################################
# tv-ripper-helper.sh session: Tue 20 Apr 19:38:39 BST 2021

    season = 7
    season_name = 'Simpsons Season 7'
    input_directory = '/mnt/rigel_a1/data/media/dvd-rips/simpsons/s07'
    output_directory = '/mnt/rigel_a1/data/media/tv/The Simpsons/Season 07'
    series = DiscSeries(season_name, season, input_directory, output_directory)

    series.add_disc('s07-disc-1of4.iso', 1, [2,3,4,5,6,7,])
    series.add_disc('s07-disc-2of4.iso', 2, [2,3,4,5,6,7,8,])
    series.add_disc('s07-disc-3of4.iso', 3, [2,3,4,5,6,7,8,])
    series.add_disc('s07-disc-4of4.iso', 4, [37,3,4,5,6,])

    series.rip_all()

################################################################################

################################################################################
# tv-ripper-helper.sh session: Tue 20 Apr 19:42:28 BST 2021

    season = 8
    season_name = 'Simpsons Season 8'
    input_directory = '/mnt/rigel_a1/data/media/dvd-rips/simpsons/s08'
    output_directory = '/mnt/rigel_a1/data/media/tv/The Simpsons/Season 08'
    series = DiscSeries(season_name, season, input_directory, output_directory)

    series.add_disc('s08-disc-1of4.iso', 1, [36,2,3,4,5,37,])
    series.add_disc('s08-disc-2of4.iso', 2, [2,3,4,5,6,7,8,])
    series.add_disc('s08-disc-3of4.iso', 3, [2,3,4,5,6,7,8,])
    series.add_disc('s08-disc-4of4.iso', 4, [5,4,40,6,7,])

    series.rip_all()

################################################################################

    ################### END OF INPUT ###############################################

    print()
    print("Program complete")
    print("Stats:")

    endtime = datetime.datetime.now()
    duration = (endtime - starttime).total_seconds()
    print("  Program start: {}".format(starttime.strftime("%Y/%m/%d %H:%M:%S")))
    print("  Program end  : {}".format(endtime.strftime("%Y/%m/%d %H:%M:%S")))
    print("  Duration     : {:.0f}d {:.0f}h {:.0f}m {:.0f}s".format(duration // 86400, (duration // 3600) % 24, (duration // 60) % 60, duration % 60))
