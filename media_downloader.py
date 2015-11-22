"""Simple media download class that currently only handles Youtube based media"""
# Goal: Make a wrapper for the command line interface that will allow us to
# run a simple python script that makes this easier.

# Wishlist:
# 1. Keeps track of success/error
# 2. Web UI which grabs meta data (album cover, title, description)
# 3. Options hash for audio
# 4. Dropbox integration (after web UI)

from collections import defaultdict
from urllib.parse import urlparse
import pafy
import subprocess
import os
import validators

class Downloader:
    """Download class for youtube (Refactor)"""
    def __init__(self):
        self.stats = self.initialize_stats_hash()
        self.execute()

    def execute(self):
        """Save user inputted URL as the download source."""
        self.url = self.get_url()
        self.media_type = self.parse_media_type()
        self.download_format = self.select_download_format()
        self.download()

    @classmethod
    def initialize_stats_hash(cls):
        """Initializes a dictionary to keep track of download information"""
        stats = {'download_stats': defaultdict(int), 'failed_urls': [], 'downloaded_urls': []}
        return stats

    def get_url(self):
        """Ask for a URL until a valid one is inputted"""
        while True:
            current_url = input('Please input the URL.\n\n>>>  ').strip()
            if self.validate_url(current_url):
                break
            else:
                print("That is not a valid YouTube URL. Please try again.")
                continue

        return current_url


    def parse_media_type(self):
        """Loosely check what the URL links to by searching the url for keywords"""
        supported_media_types = {'watch': 'media', 'playlist': 'playlist', 'channel': 'channel'}
        for media_type in supported_media_types.keys():
            if media_type in self.url:
                print("URL is detected to be a {}".format(media_type))
                return supported_media_types[media_type]
        print("Error: Unknown media type!")

    def download(self):
        """Main download method that downloads by media type and media format"""
        download_method = "download_{}".format(self.media_type)
        if callable(download_method):
            getattr(self, download_method)
        else:
            print("{} downloads are currently not supported.".format(self.media_type))

    @classmethod
    def select_download_format(cls):
        """Asks for download format (audio, video, etc)"""
        valid_formats = {'audio', 'video', 'both'}
        while True:
            desired_format = input('Would you like to download the audio, video, or both?').strip()
            if desired_format in valid_formats:
                break
            else:
                print('{} is not a valid format.'.format(desired_format))
                continue

        return desired_format

    def m4a_to_mp3(self, path):
        """Replaces a .m4a audio file with a .mp3 audio file"""
        mp3_directory = self.create_download_path('~/Downloads/media_downloads/mp3/')
        if path.endswith('m4a'):
            subprocess.call(
                ["ffmpeg", "-i", path,
                 "-acodec", "libmp3lame", "-ab", "256k",
                 os.path.join(mp3_directory, "{}mp3".format(self.file_name(path)[:-3]))] # refactor
            )
            # delete old unformatted files.
        else:
            print("{} is in the incorrect format.".format(self.file_name(path)))

    def format_audio(self, path, audio_format='mp3'):
        """Reformats the audio into a given audio_format"""
        audio_formats = {'mp3': self.m4a_to_mp3(path)}
        try:
            audio_formats[audio_format]
        except KeyError:
            print("Audio format not recognized for file: {}".format(self.file_name(path)))

    def download_audio(self, media_item):
        """Downloads audio(.m4a) and reformats to the mp3 file"""
        best_audio_m4a = media_item.getbestaudio('m4a').url
        if best_audio_m4a:
            raw_audio = best_audio_m4a.download(self.create_download_path())
            self.format_audio(raw_audio)
        else:
            print("Download failed for {}".format(self.url))

    def download_by_format(self, media_item):
        """Downloads the media item by given media format"""
        # download_formats = {'audio': self.download_audio(media_item), 'video': self.download_}
        # download_formats[self.download_format]

    # Download types

    def download_media(self):
        """Downloads a single media item"""
        media_item = pafy.new(self.url)
        print("Downloading the {} from {}".format(self.download_format, self.url))
        self.download_by_format(media_item)

    def download_channel(self):
        """Download everything from a given channel"""
        raise NotImplementedError

    def download_playlist(self):
        """Downloads media items within a playlist"""
        playlist = pafy.get_playlist(self.url)
        media_count = len(playlist['items'])
        print("Downloading {} items from {}".format(media_count, playlist['title']))
        for i, media in enumerate(playlist['items']):
            print("Downloading {} / {}.".format(i + 1, media_count))
            self.download_by_format(media['pafy'])

    # Helper methods

    @staticmethod
    def create_download_path(path='~/Downloads/media_downloads/'):
        """Creates the download path and returns the path"""
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @staticmethod
    def validate_url(url):
        """Validates that the URL is from YouTube and is a valid URL"""
        return validators.url(url) and 'youtube' in urlparse(url).netlog

    @staticmethod
    def file_name(path):
        """Returns the file name for a given file path."""
        return os.path.basename(path)

if __name__ == "__main__":
    Downloader()
