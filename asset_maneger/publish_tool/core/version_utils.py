import os
import re
import logging


class VersionUtils:
    @staticmethod
    def _get_version_pattern(base_name, suffix=None, ext=".ma"):
        """
        Creates a regex pattern to match versioned file names.

        Returns:
            Compiled regex pattern.
        """
        if suffix:
            pattern = rf"{re.escape(base_name)}_{re.escape(suffix)}_v(\d+){re.escape(ext)}$"
        else:
            pattern = rf"{re.escape(base_name)}_v(\d+){re.escape(ext)}$"
        return re.compile(pattern, re.IGNORECASE)

    @staticmethod
    def find_latest_version(path, base_name, suffix=None, ext=".ma"):
        """
        Finds the latest versioned file in the given path.

        Args:
            path (str): Directory to search.
            base_name (str): Base name like 'da'.
            suffix (str or None): Optional suffix like 'modeling'.
            ext (str): File extension (default: '.ma').

        Returns:
            tuple: (latest_version (int), file_name (str)) or (None, None).
        """
        if not os.path.isdir(path):
            logging.error(f"Path does not exist: {path}")
            return None, None

        pattern = VersionUtils._get_version_pattern(base_name, suffix, ext)

        versions = [
            (int(match.group(1)), fname)
            for fname in os.listdir(path)
            if (match := pattern.match(fname))
        ]

        if not versions:
            return None, None

        return max(versions, key=lambda x: x[0])

    @staticmethod
    def update_version(path, base_name, suffix=None, ext=".ma", padding=3):
        """
        Generates the next versioned file name and full path.

        Args:
            path (str): Target directory.
            base_name (str): Asset name.
            suffix (str or None): Optional suffix.
            ext (str): Extension (default: '.ma').
            padding (int): Zero padding for version number.

        Returns:
            tuple: (full_path (str), file_name (str))
        """
        latest_version, _ = VersionUtils.find_latest_version(path, base_name, suffix, ext)
        next_version = (latest_version + 1) if latest_version is not None else 1

        version_str = f"v{next_version:0{padding}d}"
        name_parts = [base_name, suffix, version_str] if suffix else [base_name, version_str]
        file_name = "_".join(filter(None, name_parts)) + ext

        return os.path.join(path, file_name), file_name, version_str


def main():
    path = r"E:\projects\showreel_2025\publish\da\modeling\character\ma"
    base_name = "da"
    suffix = "modeling"
    ext = ".ma"

    # Optional: Configure logging
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

    # Get latest version
    version, latest_file = VersionUtils.find_latest_version(path, base_name, suffix, ext)
    if version is not None:
        logging.info(f"Latest version: v{version:03d} -> {latest_file}")
    else:
        logging.info("No versioned files found.")

    # Get next version
    full_path, next_file = VersionUtils.update_version(path, base_name, suffix, ext)
    logging.info(f"Next file: {next_file}")
    logging.info(f"Full path: {full_path}")


if __name__ == "__main__":
    main()
