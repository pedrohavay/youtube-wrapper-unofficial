import os
import json
from urllib.parse import parse_qs

import requests
from selenium import webdriver

from youtube_wrapper_unofficial.src.youtube_engine import YoutubeEngine

class VideoProcess(YoutubeEngine):
    def __init__(self, video_id, headless=False):
        # Init parent class
        super().__init__(headless)

        # Set video id
        self.video_id = video_id

    def get_video_info_old(self, player_config=True, user_agent=False):
        # Prepare URL
        video_info_url = f"https://www.youtube.com/get_video_info?&video_id={self.video_id}"
        
        # Init headers
        headers = {}

        # Check user agent 
        if user_agent:
            headers['User-Agent'] = user_agent

        # Make GET Request
        content = requests.get(video_info_url, headers=headers)

        # Parsing query string
        query = parse_qs(content.text)

        # Parse JSON in "player_response"
        query['player_response'][0] = json.loads(query['player_response'][0])

        # Return Data
        return query['player_response'][0] if player_config else query

    def get_video_info(self, player_config=True, user_agent=False):
        # Get player data
        player_data = self.get_player_data(f"/watch?v={self.video_id}")

        # Check player data
        if player_data:
            # Get args
            player_data = player_data['config']['args']

            # Check if exists 'player_response'
            if 'player_response' in player_data.keys():
                # loads json
                player_data= json.loads(player_data['player_response'])
        else:
            player_data = False

        # Return Data
        return player_data

    def similar_videos(self):
        # Get initial data
        initial_data = self.get_initial_data(f"/watch?v={self.video_id}")

        # Set contents
        contents = initial_data['contents']

        #############################
        # Obtain Similar Video List #
        #############################

        # Init Video List
        video_list = []

        # Check contents field
        if "twoColumnSearchResultsRenderer" in contents.keys():
            data = initial_data['contents']['twoColumnSearchResultsRenderer']['primaryContents'] # Split because for line size
            data = data['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']

            # Iterate in video list
            for item in data:
                # Check if is video renderer
                if "videoRenderer" in item.keys():
                    # Appen to video list
                    video_list.append(item['videoRenderer'])

        elif "twoColumnWatchNextResults" in contents.keys():
            data = initial_data['contents']['twoColumnWatchNextResults']['secondaryResults'] # Split because for line size
            data = data['secondaryResults']['results']

            # Iterate in video list
            for item in data:
                # Check if is video renderer
                if "compactVideoRenderer" in item.keys():
                    # Appen to video list
                    video_list.append(item['compactVideoRenderer'])

        # Return Video List
        return video_list
