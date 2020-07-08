import os
import json
from math import ceil
from urllib.parse import parse_qs, quote_plus

import lxml
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from youtube_wrapper_unofficial.src.youtube_engine import YoutubeEngine

class PlatformAction(YoutubeEngine):
    def __init__(self, headless=False):
        # Init parent class
        super().__init__(headless)

    def get_trends(self, country="US"):
        # Get initial data
        initial_data = self.get_initial_data(f"/feed/trending?gl={country}")

        # Set contents
        contents = initial_data['contents']

        #############################
        # Obtain Similar Video List #
        #############################

        # Init Video List
        video_list = {
            "trends": [],
            "recents_trends": []
        }

        # Check contents field
        if "twoColumnBrowseResultsRenderer" in contents.keys():
            # Split because for line size
            data = initial_data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]
            data = data['tabRenderer']['content']['sectionListRenderer']['contents']

            # Trends
            trends = data[0]['itemSectionRenderer']['contents'][0]['shelfRenderer']
            trends = trends['content']['expandedShelfContentsRenderer']['items']

            # Recently Trends
            recents_trends = data[1]['itemSectionRenderer']['contents'][0]['shelfRenderer']
            recents_trends = recents_trends['content']['expandedShelfContentsRenderer']['items']

            # Iterate in trends list
            for item in trends:
                # Check if is video renderer
                if "videoRenderer" in item.keys():
                    # Appen to video list
                    video_list['trends'].append(item['videoRenderer'])
            
            # Iterate in recents trends list
            for item in recents_trends:
                # Check if is video renderer
                if "videoRenderer" in item.keys():
                    # Appen to video list
                    video_list['recents_trends'].append(item['videoRenderer'])

        # Return Video List
        return video_list

    def get_filters(self):
        # Temporary Webdriver
        with webdriver.Chrome(
            chrome_options=self.options,
            executable_path=self._executable
            ) as driver:
            # Prepare Youtube URL
            yt_url = f"https://www.youtube.com/results?search_query=replaceterm"

            # Open this video
            driver.get(yt_url)

            # Wait filter element be loaded
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ytd-toggle-button-renderer.ytd-search-sub-menu-renderer')))

            # Open filter search menu
            driver.find_element_by_css_selector("ytd-toggle-button-renderer.ytd-search-sub-menu-renderer").click()

            # Init HTML parser
            html = BeautifulSoup(driver.page_source, "lxml")

            # Set CSS Selector
            filter_items = html.select("iron-collapse.ytd-search-sub-menu-renderer .yt-simple-endpoint")

            # Reset (or start) filter list
            self.filters = []

            # Get each filter item
            for filter_item in filter_items:
                # Add filter name to filter list
                self.filters.append(filter_item.getText().strip())

            # Return filters
            return self.filters
    
    def __filter_search(self, filters_list):
        # Check if all filters passed exists in filters
        if all(elem in self.filters for elem in filters_list):
            # Temporary Webdriver
            with webdriver.Chrome(
                chrome_options=self.options,
                executable_path=self._executable
                ) as driver:
                # Prepare Youtube URL
                yt_url = "https://www.youtube.com/results?search_query=replaceterm"

                for item in filters_list:
                    # Open this video
                    driver.get(yt_url)

                    # Wait filter element be loaded
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ytd-toggle-button-renderer.ytd-search-sub-menu-renderer')))

                    # Open filter search menu
                    driver.find_element_by_css_selector("ytd-toggle-button-renderer.ytd-search-sub-menu-renderer").click()

                    # Init HTML parser
                    html = BeautifulSoup(driver.page_source, "lxml")

                    # Set CSS Selector
                    filter_items = html.select("iron-collapse.ytd-search-sub-menu-renderer .yt-simple-endpoint", href=True)

                    # Get each filter item
                    for filter_item in filter_items:
                        # Add filter name to filter list
                        if item == filter_item.getText().strip():
                            # Returns endpoint url
                            yt_url = f"https://www.youtube.com/{filter_item['href']}"

                # Returns url final
                return yt_url
        else:
            raise Exception("Filter not exists.")


    def search(self, term, filters=None, page=1):
        # Init data
        search_data = {}

        # Enconding term to URL Encode Plus
        term_param = quote_plus(term)

        # Initial url
        yt_url = f"https://www.youtube.com/results?search_query={term_param}"

        # Check if filters exists
        # if filters is not None:
            # # Get youtube filter url
            # yt_url = self.__filter_search(filters)

            # # Replace with term
            # yt_url = yt_url.replace("replaceterm", term_param)

        # Add page query param to URL
        # yt_url = f"{yt_url}&p={page}"
        
        # Temporary Webdriver
        with webdriver.Chrome(
            chrome_options=self.options,
            executable_path=self._executable
            ) as driver:

            # Check if filters exists
            if filters is not None:
                # Get each filter passed
                for item in filters:
                    # Open this video
                    driver.get(yt_url)

                    # Wait filter element be loaded
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ytd-toggle-button-renderer.ytd-search-sub-menu-renderer')))

                    # Open filter search menu
                    driver.find_element_by_css_selector("ytd-toggle-button-renderer.ytd-search-sub-menu-renderer").click()

                    # Init HTML parser
                    html = BeautifulSoup(driver.page_source, "lxml")

                    # Set CSS Selector
                    filter_items = html.select("iron-collapse.ytd-search-sub-menu-renderer .yt-simple-endpoint", href=True)

                    # Get each filter item
                    for filter_item in filter_items:
                        # Add filter name to filter list
                        if item == filter_item.getText().strip():
                            # Returns endpoint url
                            yt_url = f"https://www.youtube.com/{filter_item['href']}"

                            # Add page query param to URL
                            yt_url = f"{yt_url}&p={page}"

            # Get page
            driver.get(yt_url)

            # Get ytInitialData
            initial_data = driver.execute_script("return window.ytInitialData;")
            
            # Set total of pages and total videos found
            search_data['term'] = term
            search_data['total'] = int(initial_data['estimatedResults'])
            search_data['pages'] = ceil(int(initial_data['estimatedResults']) / 20)
            search_data['current_page'] = page

            # Set contents from initial data
            contents = initial_data['contents']

            # Init video list in data
            search_data['videos'] = []
            search_data['channels'] = []

            # Get videos items
            if "twoColumnSearchResultsRenderer" in contents.keys():
                data = initial_data['contents']['twoColumnSearchResultsRenderer']['primaryContents'] # Split because for line size
                data = data['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']

                # Iterate in video list
                for item in data:
                    # Check if is video renderer
                    if "videoRenderer" in item.keys():
                        # Appen to video list
                        search_data['videos'].append(item['videoRenderer'])

                    # Check if is video renderer
                    if "channelRenderer" in item.keys():
                        # Appen to video list
                        search_data['channels'].append(item['channelRenderer'])

            # Returns data
            return search_data


