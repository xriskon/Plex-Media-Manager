#! /usr/utils/env python3

"""
Plex Media Manager: Organize your media library
"""

import sys
import plex_librarian

if __name__ == "__main__":
    # Check if the user is using the correct version of Python
    python_version = sys.version.split()[0]

    if sys.version_info < (3, 6):
        print("Plex Media Manager requires Python 3.6+\nYou are using Python %s, which is not supported by Plex Media Manager" % python_version)
        sys.exit(1)

    plex_librarian.main()
