import os
import logging
from typing import Optional, Tuple

class DirectoryUtils:
    @staticmethod
    def create_dir(base_path, folder_name):
        """
        Creates a subdirectory inside the specified base path.

        Args:
            base_path (str): The root directory in which to create the new folder.
            folder_name (str): The name of the folder to create.

        Returns:
            str: The full path to the created folder, or None if creation fails.
        """
        full_path = os.path.join(base_path, folder_name)
        try:
            os.makedirs(full_path, exist_ok=True)
            return full_path
        except Exception as e:
            logging.error(f"[DirectoryUtils] Failed to create directory '{full_path}': {e}")
            return None

    @staticmethod
    def create_publish_dir_structure(
        project_root: str,
        asset_name: str,
        department: str,
        asset_type: str,
        format_type: str
    ) -> Optional[Tuple[str, str, str]]:
        """
        Creates a nested directory structure for publishing an asset in a VFX pipeline.

        Final structure:
            <project_root>/
                publish/
                    <asset_type>/
                        <asset_name>/
                            <department>/
                                data/
                                    metadata/
                                    preview_image/
                                <format_type>/

        Args:
            project_root (str): Base project path (e.g., 'E:/projects/showreel_2025')
            asset_name (str): Asset name (e.g., 'tree')
            department (str): Department name (e.g., 'Model', 'Rig')
            asset_type (str): Asset type/category (e.g., 'Prop', 'Character')
            format_type (str): Output format folder (e.g., 'ma', 'usd', 'abc')

        Returns:
            Optional[Tuple[str, str, str]]: A tuple containing the full paths to the
            format_type, metadata, and preview_image folders, or None on failure.
        """

        # Input validation
        if not all([project_root, asset_type, asset_name, department, format_type]):
            logging.error("[DirectoryUtils] One or more required arguments are empty.")
            return None

        # Base path up to the department level
        base_path_chain = [
            "publish",
            asset_type,
            asset_name,
            department
        ]

        department_path = project_root
        for folder in base_path_chain:
            department_path = DirectoryUtils.create_dir(department_path, folder)
            if not department_path:
                logging.error(f"[DirectoryUtils] Failed to create directory at step: {folder}")
                return None

        # Create the format_type directory
        file_publish_path = DirectoryUtils.create_dir(department_path, format_type)
        if not file_publish_path:
            logging.error(f"[DirectoryUtils] Failed to create format_type directory.")
            return None

        # Create the data directory and its subdirectories
        data_path = DirectoryUtils.create_dir(department_path, "data")
        if not data_path:
            logging.error(f"[DirectoryUtils] Failed to create data directory.")
            return None

        metadata_path = DirectoryUtils.create_dir(data_path, "metadata")
        if not metadata_path:
            logging.error(f"[DirectoryUtils] Failed to create metadata directory.")
            return None

        preview_image_path = DirectoryUtils.create_dir(data_path, "preview_image")
        if not preview_image_path:
            logging.error(f"[DirectoryUtils] Failed to create preview_image directory.")
            return None

        return file_publish_path, metadata_path, preview_image_path


