"""This files contains the agent used to communicate with TMDB."""

import json
import os
import requests
from utils.tools import *


class TMDB:
    def __init__(self, config):
        self.key = config.get("tmdb").get("apikey")
        self.headers = {
            "accept": "application/json",
            "Authorization": F"Bearer {self.key}"
        }
        self.image_language = config.get("tmdb").get("image_language")

    def get_poster(self, tmdb_id, media_type):
        """Get the poster URL."""
        if media_type == "movie":
            url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/images?include_image_language={self.image_language}"
        elif media_type == "show":
            url = f"https://api.themoviedb.org/3/tv/{tmdb_id}/images?include_image_language={self.image_language}"
        else:
            return None

        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                posters = json.loads(response.content).get("posters")
                return posters[0].get("file_path")
        except Exception as e:
            return None

    def get_backdrop(self, tmdb_id, media_type):
        if media_type == "movie":
            url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/images?include_image_language=en%2Cnull"
        elif media_type == "show":
            url = f"https://api.themoviedb.org/3/tv/{tmdb_id}/images?include_image_language=en%2Cnull"
        else:
            return None

        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                posters = json.loads(response.content).get("backdrops")
                return posters[0].get("file_path")
        except Exception as e:
            return None

    def get_trailer(self, tmdb_id, media_type, language="en-US"):
        if media_type == "movie":
            url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/videos?language={language}"
        elif media_type == "show":
            url = f"https://api.themoviedb.org/3/tv/{tmdb_id}/videos?language={language}"
        else:
            return None

        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                videos = json.loads(response.content).get("results")
                trailers = [obj for obj in videos if obj["type"] == "Trailer"]
                if len(trailers) == 1:
                    return trailers[0].get("key")
                sorted_trailers = sorted(trailers, key=lambda x: x["size"])
                for trailer in sorted_trailers:
                    if self._find_official_trailer(trailer.get("name")):
                        return trailer.get("key")
                return sorted_trailers[0].get("key")

        except Exception as e:
            return None

    def search(self, title, release_year=None, media_type=None, tmdb_id=None, include_adult=True, language="en-US"):
        """
        Search for a movie/TV Show in TMDB

        Args:
            title (str): Title of the movie/TV show
            release_year (int): Primary release year of the movie/TV show
            media_type (str): The type of the media provided (movie OR show)
            tmdb_id (int): The ID of the movie/TV show
            include_adult (bool): Include adult content in search
            language (str): The main language of the media
        Returns:
            int: The ID of the movie/TV show
        """
        if media_type is None:
            return None
        elif media_type == "movie":
            return self.search_movie(title, release_year, tmdb_id, include_adult, language)
        elif media_type == "show":
            return self.search_show(title, release_year, tmdb_id, include_adult, language)
        else:
            return None

    def search_movie(self, movie_title, release_year=None, tmdb_id=None, include_adult=True, language="en-US"):
        if tmdb_id:
            return self._search_movie_id(tmdb_id, language)
        else:
            return self._search_movie_title(movie_title, release_year, include_adult, language)

    def search_show(self, movie_title, release_year=None, tmdb_id=None, include_adult=True, language="en-US"):
        if tmdb_id:
            return self._search_show_id(tmdb_id, language)
        else:
            return self._search_show_title(movie_title, release_year, include_adult, language)

    def _search_show_id(self, tmdb_id, language="en-US"):
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?language={language}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                result = json.loads(response.content)
                return result.get("id")
        except Exception as e:
            print(e)
            return None

    def _search_show_title(self, show_title, release_year=None, include_adult=True, language="en-US"):
        url = f"https://api.themoviedb.org/3/search/tv?query={show_title}&first_air_date_year={release_year}&include_adult={include_adult}&language={language}&page=1"

        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                result = json.loads(response.content).get("results")[0]
                return result.get("id")
        except Exception as e:
            print(e)
            return None

    def _search_movie_id(self, tmdb_id, language="en-US"):
        url = f"https://api.themoviedb.org/3/tv/{tmdb_id}?language={language}"

        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                result = json.loads(response.content)
                return result.get("id")
        except Exception as e:
            print(e)
            return None

    def _search_movie_title(self, movie_title, release_year=None, include_adult=True, language="en-US"):
        url = f"https://api.themoviedb.org/3/search/movie?query={movie_title}&include_adult={include_adult}&language={language}&primary_release_year={release_year}&page=1"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                result = json.loads(response.content).get("results")[0]
                return result.get("id")
        except Exception as e:
            print(e)
            return None

    def _find_official_trailer(self, name):
        if "official trailer" in name.lower():
            return True
        return False  # Return None if no match is found
