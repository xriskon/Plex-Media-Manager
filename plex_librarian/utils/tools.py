"""This file contains miscellaneous functions used throughout the code"""

import shutil
import subprocess
from datetime import datetime
import Levenshtein
from pytube import YouTube
import os
import re
import requests


def validate_name(filename):
    """
    Validate a filename for renaming a file.
    """
    # Check if the filename is empty
    if not filename.strip():
        return None

    # Check if the filename contains any invalid characters
    invalid_chars = '/\\?%*:|"<>'
    for char in invalid_chars:
        filename = filename.replace(char, '')

    # Check if the filename is too long
    if len(filename) > 255:  # Maximum filename length for most filesystems
        filename = filename[:255]

    # Check for reserved filenames (e.g., Windows)
    reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5',
                      'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5',
                      'LPT6', 'LPT7', 'LPT8', 'LPT9']
    if filename.upper() in reserved_names:
        filename = filename + '_'

    # If all checks pass, return the validated filename
    return filename


def get_string_similarity(str1, str2):
    """
    Check similarity of two strings.

    Args:
        str1 (str): String 1 to check.
        str2 (str): String 2 to check.

    Returns:
        int: The number of characters required to change for the two strings to match
    """
    str1 = str1.capitalize()
    str2 = str2.capitalize()
    return Levenshtein.distance(str1, str2)


def get_media(sections):
    # GET MEDIA
    media = {}
    for item in sections:
        _type = item.get("type")
        paths = item.get("path")
        section_files_and_folders = []
        for path in paths:
            folders_files = os.listdir(path)
            for entry in folders_files:
                full_path = os.path.join(path, entry)
                if os.path.isdir(full_path) or (os.path.isfile(full_path) and is_video_file(entry)):
                    section_files_and_folders.append(full_path)
        media[_type] = section_files_and_folders
    return media


def get_movie_title(filename):
    # Regular expression patterns to match different naming conventions
    patterns = [
        r'(?P<title>.+?)\s*\((?P<year>\d{4})\)\s*{tmdb-(?P<tmdb_id>\d+)}',
        r'(?P<title>.+?)\s*\((?P<year>\d{4})\)',
        r'(?P<title>.+?)\s*\((?P<year>\d{4})\)\s*-\s*(?P<resolution>\d+p)',
        r'(?P<title>.+?)\.(?P<year>\d{4})\.(?P<resolution>\d+p)',
        r'(?P<title>.+?)\s*\((?P<year>\d{4})\)\s*-\s*(?P<codec>[a-zA-Z0-9]+)',
        r'(?P<title>.+?)\.(?P<year>\d{4})\.(?P<codec>[a-zA-Z0-9]+)',
        r'(?P<title>.+?)\s*\((?P<year>\d{4})\)\s*-\s*(?P<language>[a-zA-Z]+)',
        r'(?P<title>.+?)\.(?P<year>\d{4})\.(?P<language>[a-zA-Z]+)',
        r'(?P<title>.+?)\.(?P<year>\d{4})\s*{tmdb-(?P<tmdb_id>\d+)}',
    ]

    result = {}
    for pattern in patterns:
        match = re.match(pattern, filename)
        if match:
            result.update({
                'title': match.group('title').replace('.', ' '),
                'year': int(match.group('year')),
                'resolution': match.group('resolution') if 'resolution' in match.groupdict() else None,
                'codec': match.group('codec') if 'codec' in match.groupdict() else None,
                'language': match.group('language') if 'language' in match.groupdict() else None,
                'tmdb_id': int(match.group('tmdb_id')) if 'tmdb_id' in match.groupdict() else None
            })
            break  # Stop after first match

    # Return collected information, if any
    return result or None


def get_show_title(filename):
    # Regular expression patterns to match different naming conventions
    patterns = [
        r'(?P<title>.+?)\.S(?P<season>\d{2})',
        r'(?P<title>.+?)\s*\((?P<year>\d{4})\)',
        r'(?P<title>.+?)\.S(?P<season>\d{2})E(?P<episode>\d{2})',
        r'(?P<title>.+?)\s*-\s*S(?P<season>\d{2})E(?P<episode>\d{2})',
        r'(?P<title>.+?)\.S(?P<season>\d{2})E(?P<episode>\d{1,2})',
        r'(?P<title>.+?)\.(?P<year>\d{4})\.(?P<month>\d{2})\.(?P<day>\d{2})',
        r'(?P<title>.+?)\.Season(?P<season>\d+)',
        r'(?P<title>.+?)\.S(?P<season>\d{2})',
        r'(?P<title>.+?)\s*Complete',
    ]

    for pattern in patterns:
        match = re.match(pattern, filename)
        if match:
            return {
                'title': match.group('title').replace('.', ' '),
                'season': int(match.group('season')) if 'season' in match.groupdict() else None,
                'episode': int(match.group('episode')) if 'episode' in match.groupdict() else None,
                'year': int(match.group('year')) if 'year' in match.groupdict() else None,
                'month': int(match.group('month')) if 'month' in match.groupdict() else None,
                'day': int(match.group('day')) if 'day' in match.groupdict() else None,
                'complete': True if 'Complete' in match.group() else False
            }

    # If no pattern matches, return None
    return None


def is_image_file(filename):
    """
    Check if a file has an image extension.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file has an image extension, False otherwise.
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']  # Add more extensions if needed
    lowercase_filename = filename.lower()

    # Check if the filename ends with any of the video extensions
    for ext in image_extensions:
        if lowercase_filename.endswith(ext):
            return True  # If extension found, return True
    return False


def is_video_file(filename):
    """
    Check if a file has a video extension.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file has a video extension, False otherwise.
    """
    video_extensions = ['.mp4', '.mkv', '.mpg', '.mov', '.webm']  # Add more extensions if needed
    lowercase_filename = filename.lower()

    # Check if the filename ends with any of the video extensions
    for ext in video_extensions:
        if lowercase_filename.endswith(ext):
            return True  # If extension found, return True
    return False


def is_valid_name(filename):
    """
    Check if a file has a valid name.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file has a valid name, False otherwise.
    """
    pattern = r'(.+)\s\((\d{4})\)\s\{tmdb-(\d+)\}'

    # Check if pattern matches the name
    match = re.match(pattern, filename)
    if match:
        return True
    else:
        return False


def has_poster(directory):
    """
    Check if there is a valid image in the specified folder.
    """
    for filename in os.listdir(directory):
        if filename.lower().startswith("poster") and is_image_file(filename):
            image_path = os.path.join(directory, filename)
            if os.path.getsize(image_path) != 0:
                return True
    return False


def has_backdrop(directory):
    """
    Check if there is a valid image in the specified folder.
    """
    for filename in os.listdir(directory):
        if filename.lower().startswith("backdrop") and is_image_file(filename):
            image_path = os.path.join(directory, filename)
            if os.path.getsize(image_path) != 0:
                return True
    return False


def has_trailer(filepath):
    """
    Check if a file contains a folder named "Trailers" and inside it there is a video called "Official Trailer".

    Parameters:
        filepath (str): The path to the file to check.

    Returns:
        bool: True if the conditions are met, False otherwise.
    """
    trailers_folder = os.path.join(filepath, "Trailers")
    if os.path.exists(trailers_folder) and os.path.isdir(trailers_folder):
        media_trailers = os.listdir(trailers_folder)
        for media in media_trailers:
            fullpath = os.path.join(trailers_folder, media)
            if os.path.isfile(fullpath) and is_video_file(media):
                return True
    return False


def download_image(url, destination):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(destination, 'wb') as file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, file)
    except Exception as e:
        print("Error occurred:", str(e))


def download_youtube_video(url, destination):
    """
    Download a video from YouTube and save it to the specified destination.

    Parameters:
        url (str): The URL of the YouTube video.
        destination (str): The path where the video will be saved.
    """
    try:
        yt = YouTube(url)
        video = yt.streams.filter(resolution='1080p').order_by('resolution').desc().first()
        audio = yt.streams.get_audio_only()

        # Extracting the file extension from the original filename
        original_filename = video.default_filename
        file_extension = os.path.splitext(original_filename)[1]

        # Setting the new filename to "Official Trailer" with the original file extension
        video_filename = "Official Trailer" + file_extension
        audio_filename = "Official Trailer.mp4"

        # Downloading and renaming the video file
        video.download(output_path=destination, filename=video_filename)
        audio.download(output_path=destination, filename=audio_filename)

        video_filepath = os.path.join(destination, video_filename)
        audio_filepath = os.path.join(destination, audio_filename)
        destination_filepath = os.path.join(destination, "Official Trailer" + file_extension)
        combine_audio_video(audio_file=audio_filepath, video_file=video_filepath, output_file=destination_filepath)

        print(f"Video downloaded successfully! {destination}")
    except Exception as e:
        print(f"Error: {e}")


def delete_images(directory):
    for filename in os.listdir(directory):
        if is_image_file(filename):
            # Form the absolute path to the file
            filepath = os.path.join(directory, filename)
            # Attempt to remove the file
            try:
                os.remove(filepath)
            except Exception as e:
                print(e)


def delete_trailer(directory):
    trailers_folder = os.path.join(directory, "Trailers")
    if os.path.exists(trailers_folder):
        try:
            # Remove the directory and its contents
            shutil.rmtree(trailers_folder)
        except Exception as e:
            return


def combine_audio_video(video_file, audio_file, output_file):
    # Run ffmpeg command to combine audio and video
    ffmpeg_command = [
        'ffmpeg',
        '-i', video_file,
        '-i', audio_file,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-strict', 'experimental',
        output_file
    ]
    subprocess.run(ffmpeg_command)


def is_table_empty(table):
    """
    Check if a PrettyTable object is empty.

    Parameters:
        table (PrettyTable): The PrettyTable object to check.

    Returns:
        bool: True if the table is empty, False otherwise.
    """
    table_string = table.get_string()
    # Check if the string representation of the table contains any rows of data
    return len(table_string.split('\n')) <= 6


def pprint(message):
    print(f"[{_get_time()}] {message}")


def _get_time():
    current_time = datetime.now()
    return current_time.strftime("%Y-%m-%d %H:%M:%S")
