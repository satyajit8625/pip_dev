import os
import logging

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
    ) -> str:
        """
        Creates a nested directory structure for publishing an asset in a VFX pipeline.

        Final structure:
            <project_root>/
                publish/
                    <asset_name>/
                        <department>/
                            <asset_type>/
                                <format_type>/

        Args:
            project_root (str): Base project path (e.g., 'E:/projects/showreel_2025')
            asset_name (str): Asset name (e.g., 'tree')
            department (str): Department name (e.g., 'Model', 'Rig')
            asset_type (str): Asset type/category (e.g., 'Prop', 'Character')
            format_type (str): Output format folder (e.g., 'ma', 'usd', 'abc')

        Returns:
            str: Full final path to the format_type folder, or None on failure.
        """
        # Input validation
        if not all([project_root, asset_name, department, asset_type, format_type]):
            logging.error("[DirectoryUtils] One or more required arguments are empty.")
            return None

        path_chain = [
            "publish",
            asset_name,
            department,
            asset_type,
            format_type
        ]

        current_path = project_root
        for folder in path_chain:
            current_path = DirectoryUtils.create_dir(current_path, folder)
            if not current_path:
                logging.error(f"[DirectoryUtils] Failed to create directory at step: {folder}")
                return None  # Stop if any folder creation fails
        
        return current_path
