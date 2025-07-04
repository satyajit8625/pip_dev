import os
import re
import logging


class VersionUtils:
    @staticmethod
    def strip_version(name_part):
        """
        Strips trailing version (e.g. '_v001') from a file name part if present.

        Args:
            name_part: File name without extension (e.g., 'char_v003')

        Returns:
            The name without the version suffix (e.g., 'char')
        """
        match = re.match(r"(.*)_v\d+$", name_part)
        return match.group(1) if match else name_part

    @staticmethod
    def find_latest_version(file_list, base_file_name):
        """
        Finds the latest version number of files that match the base file name pattern in a list.

        Args:
            file_list: List of file names (not paths).
            base_file_name: The base file name (e.g., 'char.ma').

        Returns:
            The highest version number found, or None if no matching versions exist.
        """
        if not file_list or not base_file_name:
            logging.warning("file_list and base_file_name must be provided.")
            return None

        name_part, ext = os.path.splitext(base_file_name)
        name_part = VersionUtils.strip_version(name_part)

        pattern = re.compile(rf"{re.escape(name_part)}_v(\d+)" + re.escape(ext) + r"$")

        latest_version_number = None

        for filename in file_list:
            match = pattern.fullmatch(filename)
            if match:
                version = int(match.group(1))
                if latest_version_number is None or version > latest_version_number:
                    latest_version_number = version

        return latest_version_number

    @staticmethod
    def update_version(file_list, base_file_name):
        """
        Builds the next versioned file name based on the highest version found in the list.

        Args:
            file_list: List of file names (e.g., from os.listdir(path)).
            base_file_name: The base file name (e.g., 'char.ma').

        Returns:
            A versioned file name like 'char_v002.ma'.
        """
        latest_version = VersionUtils.find_latest_version(file_list, base_file_name)
        next_version = (latest_version + 1) if latest_version is not None else 1

        name_part, ext = os.path.splitext(base_file_name)
        name_part = VersionUtils.strip_version(name_part)

        return f"{name_part}_v{next_version:03d}{ext}"
    