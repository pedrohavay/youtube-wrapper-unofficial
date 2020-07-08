import json

from youtube_wrapper_unofficial.src.platform_action import PlatformAction
 
if __name__ == "__main__":
    # Init Video Process
    platform = PlatformAction(headless=True)

    # Get filters item
    filters = platform.get_filters() 

    # Showing the chosen filter
    print([filters[6]])

    # Showing the search results in JSON
    print(json.dumps(platform.search("minecraft", filters=[filters[6]])))