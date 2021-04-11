#!/usr/bin/env python3
# coding=utf-8
# - SW - 11/04/2021 21:52 -
# Lay out a mapping of TV series to discs, then prompt interactively to read and convert them one by one
import subprocess
import re

class Disc:
    def __init__(self, disc_number, season_num, episode_list, starting_episode, disc_is_avail=False, disc_location=None):
        self.disc_number = disc_number
        self.season_num = season_num
        self.episode_list = episode_list
        self.required_title_count = len(episode_list)
        self.starting_episode = starting_episode
        self.disc_is_avail = disc_is_avail
        self.disc_location = disc_location
        self.next_disc_starting_episode = starting_episode + sum(episode_list)

        print("Initialised disc {} with {} required titles".format(self.disc_number, self.required_title_count))
        print("First episode {}, last {}".format(self.starting_episode, self.next_disc_starting_episode-1))

    def scan(self):
        if not self.disc_is_avail:
            raise ValueError("Cannot scan disc {} yet, not available".format(self.disc_number))
        if self.disc_location is None:
            raise ValueError("Cannot scan disc {} yet, no location".format(self.disc_number))
        print("Disk {} is scanning...".format(self.disc_number))
        result = subprocess.run(['HandBrakeCLI', '-i', self.disc_location, '-t', '0'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print("Scan complete")
        result = result.stdout.decode('utf-8')
        self.disc_scan_result = result

        self.title_count = int(re.search('libhb: scan thread found (\d+) valid title', result).group(1))
        self.title_incides = list(map(int, re.findall('^\+ title (\d+):', result, re.MULTILINE)))
        if self.title_count != len(self.title_incides):
            raise ValueError("Did not parse disc scan result correctly. Need {} good titles but got {} title indices".format(self.title_count, len(self.title_incides)))
        if self.required_title_count != self.title_count:
            print("Did not find the required {} number of good titles, found {}".format(self.required_title_count, self.title_count))
            print("Override by calling Disc.override_title_indices()")
            # TODO: Write out self.disc_scan_result to disk for use by user
        else:
            print("Found {} good titles to rip".format(self.title_count))
            print("Ready to rip disc {}".format(self.disc_number))

    def override_title_indices(self, new_title_indices):
        self.title_indices = new_title_indices
        self.title_count = len(new_title_indices)

    def rip(self):
        if self.required_title_count != self.title_count:
            raise ValueError("Do not have the required {} number of good title indices, have {}".format(self.required_title_count, self.title_count))
        print("Ripping disc {}...".format(self.disc_number))

        ep = self.starting_episode
        for i in range(0, self.title_count):
            title = self.title_incides[i]
            eps = self.episode_list[i]
            ep_string = ""
            while eps > 0:
                ep_string = ep_string + "e" + f'{ep:02}'
                eps -= 1
                ep += 1
            print("Title {} ({} of {}) - contains episodes '{}'...".format(title, i+1, self.title_count, ep_string))
            output_name = "s" + f'{self.season_num:02}' + ep_string + ".mp4"
            print("Executing command: 'HandBrakeCLI -i /dev/dvd -o {} -t {} --audio-lang-list eng'".format(output_name, title))
            input("Press ENTER when ready... ")

class DiscsForIngestion:
    def __init__(self, list_of_discs):
        self.list_of_discs = list_of_discs

    def ingest_all(self):
        for i in range(0+1,len(self.list_of_discs)+1):
            # +1 for 1-based index
            print("Ingesting disc {}:".format(i))
            disc = self.list_of_discs[i-1]
            if not disc.disc_is_avail:
                print()
                print("PLEASE INSERT DISC {}".format(i))
                input("Press ENTER when ready... ")
                # Now assume disc is changed and ready
                disc.disc_is_avail = True
            disc.scan()
            disc.rip()
            print("Finished ingesting disc {}".format(i))


if __name__ == "__main__":
    # execute only if run as a script

    season = 1
    discs = []
    discs.append(Disc(1, season, [2,1,1], 1, True, "/mnt/rigel_a1/data/media/tv-to-sort/ds9/s01/disc1.iso"))
    discs.append(Disc(2, season, [1,1,1,1], discs[-1].next_disc_starting_episode, False, "/dev/dvd"))

    season1 = DiscsForIngestion(discs)
    season1.ingest_all()

