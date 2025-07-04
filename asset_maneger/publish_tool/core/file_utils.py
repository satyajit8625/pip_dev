import os
import logging


class DirectoryUtils:
    @staticmethod
    def create_dir(base_path, folder_name):
        """
        Creates a directory at the given base path with the specified folder name.

        Args:
            base_path: The root directory where the folder should be created.
            folder_name: The name of the folder to create.

        Returns:
            The full path to the created (or existing) folder.
        """
        full_path = os.path.join(base_path, folder_name)

        try:
            os.makedirs(full_path, exist_ok=True)
            print(f"Directory created (or already exists): {full_path}")
            return full_path
        except Exception as e:
            logging.error(f"Error creating directory: {e}")
            return None

    @staticmethod
    def create_publish_structure(publish_root, asset_name, department, asset_type, format_type):
        """
        Creates a full folder structure for publishing an asset.

        Structure:
            publish_root/
                asset_name/
                    department/
                        asset_type/
                            asset_name/
                                format_type/

        Args:
            publish_root: Root directory for publishing (e.g., 'C:/project/publish')
            asset_name: Asset name (e.g., 'char_main')
            department: Department name (e.g., 'modeling')
            asset_type: Asset type (e.g., 'character', 'prop')
            format_type: Format folder (e.g., 'ma', 'usd', 'abc')

        Returns:
            The final full path to the format_type folder.
        """
        asset_dir = DirectoryUtils.create_dir(publish_root, asset_name)
        if not asset_dir:
            return None

        dept_dir = DirectoryUtils.create_dir(asset_dir, department)
        if not dept_dir:
            return None

        type_dir = DirectoryUtils.create_dir(dept_dir, asset_type)
        if not type_dir:
            return None

        nested_asset_dir = DirectoryUtils.create_dir(type_dir, asset_name)
        if not nested_asset_dir:
            return None

        final_publish_path = DirectoryUtils.create_dir(nested_asset_dir, format_type)
        return final_publish_path
