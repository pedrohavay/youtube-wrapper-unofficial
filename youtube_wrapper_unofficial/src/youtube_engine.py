import os
import json

import requests
from selenium import webdriver

from urllib.parse import parse_qs

class YoutubeEngine:
    # Variable Configuration
    EXECUTABLE_FILENAME="chromedriver"

    def __init__(self, headless=False):
        # Create webdrive config
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('no-sandbox')
        self.options.add_argument('disable-dev-shm-usage')

        # Check headless param
        if headless:
            self.options.add_argument("headless")

    @property
    def _executable(self):
        # Get current file path
        current_path = os.path.dirname(os.path.abspath(__file__))

        # Get executable path
        executable_path = os.path.abspath(os.path.join(
            current_path,
            '..',
            'bin',
            self.EXECUTABLE_FILENAME
        ))

        # Return chromedrive path
        return executable_path

    def get_initial_data(self, url):
        # Temporary Webdriver
        with webdriver.Chrome(
            chrome_options=self.options,
            executable_path=self._executable
            ) as driver:
            # Prepare Youtube URL
            yt_url = f"https://www.youtube.com{url}"

            # Open this video
            driver.get(yt_url)

            # Get Youtube Initial Data
            yt_initial_data = driver.execute_script("return window.ytInitialData;")

            # Return Data
            return yt_initial_data
    
    def get_player_data(self, url):
        # Temporary Webdriver
        with webdriver.Chrome(
            chrome_options=self.options,
            executable_path=self._executable
            ) as driver:
            # Prepare Youtube URL
            yt_url = f"https://www.youtube.com{url}"

            # Open this video
            driver.get(yt_url)

            # Get Youtube Initial Data
            yt_player_data = driver.execute_script("return window.ytplayer;")

            # Return Data
            return yt_player_data