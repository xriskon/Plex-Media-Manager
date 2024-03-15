#! /usr/bin/env python3
"""
This module contains the main logic to download and organize any Plex Media Library.
"""

import sys
from prettytable import PrettyTable
from progress.bar import ShadyBar
from services.plex import Plex
from services.tmdb import TMDB
from utils import artwork
from utils.tools import *
from config import load_config


config_file = load_config()
if config_file is None:
    sys.exit(1)
plex = Plex(config_file)
tmdb = TMDB(config_file)


def get_posters():
    """
    Download all the posters
    """
    sections = plex.get_sections()
    media = get_media(sections)
    missing_poster = {}
    for entry in media:
        section_media = media.get(entry)
        missing_in_section = []
        for item in section_media:
            if not has_poster(item):
                missing_in_section.append(item)
        missing_poster[entry] = missing_in_section

    table = PrettyTable()
    table.title = "Failed Downloads"
    table.field_names = ["Title", "Release Year", "TMDB ID", "Type"]
    for entry in missing_poster:
        # GET THE MEDIA IN CURRENT WORKING SECTION
        section_media = missing_poster.get(entry)
        # IF LIST IS EMPTY(NO MISSING POSTER)
        if not section_media:
            continue

        print(f"Starting download for '{entry}'")
        # START PROGRESS BAR
        with ShadyBar('Downloading', fill='#', suffix='%(percent).1f%% - %(eta)ds', max=len(missing_poster.get(entry))) as bar:
            for item in section_media:
                filename = os.path.basename(item)
                if entry == "movie":
                    info = get_movie_title(filename)
                elif entry == "show":
                    info = get_show_title(filename)
                else:
                    continue
                title = info.get("title")
                year = info.get("year")
                tmdb_id = info.get("tmdb_id")

                # IF TMDB_ID IS MISSING -> SEARCH TMDB
                if tmdb_id is None:
                    tmdb_id = tmdb.search(title, year, media_type=entry)

                image = tmdb.get_poster(tmdb_id, media_type=entry)
                if image is None:
                    table.add_row([title, year, tmdb_id, entry])
                    bar.next()
                    continue
                image_url = f"https://image.tmdb.org/t/p/original{image}"
                image_ext = os.path.splitext(image)[1]
                poster_path = os.path.join(item, f"poster{image_ext}")
                download_image(image_url, poster_path)
                bar.next()
    if not is_table_empty(table):
        print(table)
        return


def get_backdrops():
    """
    Download all the backdrops.
    """
    sections = plex.get_sections()
    media = get_media(sections)
    missing_poster = {}
    for entry in media:
        section_media = media.get(entry)
        missing_in_section = []
        for item in section_media:
            if not has_backdrop(item):
                missing_in_section.append(item)
        missing_poster[entry] = missing_in_section

    table = PrettyTable()
    table.title = "Failed Downloads"
    table.field_names = ["Title", "Release Year", "TMDB ID", "Type"]
    for entry in missing_poster:
        # GET THE MEDIA IN CURRENT WORKING SECTION
        section_media = missing_poster.get(entry)
        # IF LIST IS EMPTY(NO MISSING POSTER)
        if not section_media:
            continue

        print(f"Starting download for '{entry}'")
        # START PROGRESS BAR
        with ShadyBar('Downloading', fill='#', suffix='%(percent).1f%% - %(eta)ds', max=len(missing_poster.get(entry))) as bar:
            for item in section_media:
                filename = os.path.basename(item)
                if entry == "movie":
                    info = get_movie_title(filename)
                elif entry == "show":
                    info = get_show_title(filename)
                else:
                    continue
                title = info.get("title")
                year = info.get("year")
                tmdb_id = info.get("tmdb_id")

                # IF TMDB_ID IS MISSING -> SEARCH TMDB
                if tmdb_id is None:
                    tmdb_id = tmdb.search(title, year, media_type=entry)

                image = tmdb.get_backdrop(tmdb_id, media_type=entry)
                if image is None:
                    table.add_row([title, year, tmdb_id, entry])
                    bar.next()
                    continue
                image_url = f"https://image.tmdb.org/t/p/original{image}"
                image_ext = os.path.splitext(image)[1]
                backdrop_path = os.path.join(item, f"backdrop{image_ext}")
                download_image(image_url, backdrop_path)
                bar.next()
    if not is_table_empty(table):
        print(table)
        return


def get_trailers():
    """
    Download the trailers for all media types, movies and TV shows, if they are missing
    """
    sections = plex.get_sections()
    media = get_media(sections)
    missing_trailer = {}
    for entry in media:
        section_media = media.get(entry)
        missing_in_section = []
        for item in section_media:
            _has_trailer = has_trailer(item)
            if not _has_trailer:
                missing_in_section.append(item)
        missing_trailer[entry] = missing_in_section

    table = PrettyTable()
    table.title = "Failed Downloads"
    table.field_names = ["Title", "Release Year", "TMDB ID", "Type"]
    for entry in missing_trailer:
        # GET THE MEDIA IN CURRENT WORKING SECTION
        section_media = missing_trailer.get(entry)
        # IF LIST IS EMPTY(NO MISSING POSTER)
        if not section_media:
            continue

        print(f"Starting download for '{entry}'")
        # START PROGRESS BAR
        with ShadyBar('Downloading', fill='#', suffix='%(percent).1f%% - %(eta)ds', max=len(missing_trailer.get(entry))) as bar:
            for item in section_media:
                filename = os.path.basename(item)
                if entry == "movie":
                    info = get_movie_title(filename)
                elif entry == "show":
                    info = get_show_title(filename)
                else:
                    continue
                title = info.get("title")
                year = info.get("year")
                tmdb_id = info.get("tmdb_id")

                # IF TMDB_ID IS MISSING -> SEARCH TMDB
                if tmdb_id is None:
                    tmdb_id = tmdb.search(title, year, media_type=entry)

                video_key = tmdb.get_trailer(tmdb_id, media_type=entry)
                if video_key is None:
                    table.add_row([title, year, tmdb_id, entry])
                    bar.next()
                    continue
                video_url = f"https://www.youtube.com/watch?v={video_key}"
                video_path = os.path.join(item, "Trailers")
                download_youtube_video(video_url, video_path)
                bar.next()
    if not is_table_empty(table):
        print(table)
        return


def rename_media():
    """
    Rename all media.
    """
    pass


def clear_images():
    """
    Clear all downloaded images, posters & backdrops.
    """
    sections = plex.get_sections()
    media = get_media(sections)
    for item in media:
        section_media = media.get(item)
        for entry in section_media:
            delete_images(entry)


def clear_trailers():
    """
    Clear all downloaded trailers.
    """
    sections = plex.get_sections()
    media = get_media(sections)
    for item in media:
        section_media = media.get(item)
        for entry in section_media:
            delete_trailer(entry)


def _quit():
    print("Bye!")
    sys.exit(1)


def print_logo():
    """
    Print the logo.
    """
    print(artwork.ascii_art)
    print("Created by xriskon || Christos Konstantopoulos")
    print("Version 0.1")
    print("https://github.com/xriskon\n")


def print_list():
    """
    Print the command list.
    """
    print("[1]\tGet posters")
    print("[2]\tGet backdrops")
    print("[3]\tGet trailers")
    print("[4]\tRename media")
    print("[5]\tClear images")
    print("[6]\tClear trailers")
    print("[0]\tExit")


def _clear_screen():
    # Clear screen using ANSI escape codes
    if os.name == 'posix':  # For Unix/Linux/MacOS
        os.system('clear')
    elif os.name == 'nt':   # For Windows
        os.system('cls')
    else:
        # For other operating systems, simply print newlines to clear the screen
        print('\n' * 100)


commands = {
    0: _quit,
    1: get_posters,
    2: get_backdrops,
    3: get_trailers,
    4: rename_media,
    5: clear_images,
    6: clear_trailers
}


def main():
    """
    This is main function the program runs off.
    """
    _clear_screen()
    print_logo()
    print_list()
    while True:
        while True:
            try:
                cmd = int(input("New command:"))
                break
            except ValueError as error:
                print("That's not a valid option!")
                print(error)
        _cmd = commands.get(cmd)

        if _cmd:
            _cmd()
        elif cmd == "":
            print("")
        else:
            print("That's not a valid option!")


if __name__ == "__main__":
    main()
