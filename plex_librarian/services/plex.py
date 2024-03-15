"""This files contains the agent used to communicate with Plex."""
import xmltodict
import requests
from utils.tools import *


class Plex:
    def __init__(self, config):
        self.token = config.get("plex").get("token")
        self.url = config.get("plex").get("server_url")

    def get_sections(self):
        url = f'{self.url}/library/sections'
        headers = {'X-Plex-Token': self.token}

        # Get Plex response
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return 1
        except Exception as e:
            print(e)
            return 1
        result = xmltodict.parse(response.content).get("MediaContainer").get("Directory")
        movie = {
            "type": "movie",
            "id": None,
            "path": []
        }
        show = {
            "type": "show",
            "id": None,
            "path": []
        }
        for section in result:
            paths = section.get("Location")
            for path in paths:
                if section.get("@type") == "movie":
                    movie["id"] = section.get("@key")
                    movie.get("path").append(path.get("@path"))
                elif section.get("@type") == "show":
                    show["id"] = section.get("@key")
                    show.get("path").append(path.get("@path"))

        if not movie.get("path"):
            sections = [show]
        elif not show.get("path"):
            sections = [movie]
        else:
            sections = [movie, show]
        return sections

    def get_media(self):
        pass

    def scan_library(self):
        pass

    def refresh_metadata(self, section_id):
        url = f"{self.url}/library/sections/{section_id}/refresh?force=1&X-Plex-Token={self.token}"
