# File: asset_manager/publish_tool/core/asset_scene_utils.py

import maya.cmds as mc
import datetime
import logging
from typing import Optional, Dict

class AssetSceneUtils:
    """
    Utility class for asset-related scene operations in Maya.
    Provides methods for creating metadata nodes and retrieving asset data.
    """

    METADATA_SUFFIX = "_metadata_node"
    logger = logging.getLogger("AssetSceneUtils")

    def __new__(cls, *args, **kwargs):
        raise NotImplementedError("AssetSceneUtils is a static utility class and cannot be instantiated.")

    @staticmethod
    def get_metadata_node_name() -> Optional[str]:
        """
        Returns the name of the metadata node in the scene.

        Returns:
            Optional[str]: Metadata node name if found, otherwise None.
        """
        nodes = [n for n in mc.ls(type='network') if n.endswith(AssetSceneUtils.METADATA_SUFFIX)]
        return nodes[0] if nodes else None

    @staticmethod
    def get_asset_data() -> Dict[str, str]:
        """
        Retrieves metadata from the metadata node in the scene.

        Returns:
            dict: Dictionary containing user-defined attribute names and their values.

        Raises:
            RuntimeError: If no metadata node is found.
        """
        asset_data = {}
        node = AssetSceneUtils.get_metadata_node_name()

        if not node:
            raise RuntimeError("No metadata node found in the scene.")

        user_attrs = mc.listAttr(node, userDefined=True) or []

        for attr in user_attrs:
            try:
                asset_data[attr] = mc.getAttr(f"{node}.{attr}")
            except RuntimeError as e:
                AssetSceneUtils.logger.warning(f"Could not retrieve attribute '{attr}' from '{node}': {e}")

        return asset_data

    @staticmethod
    def create_new_asset(
        department: str,
        asset_type: str,
        asset_name: str,
        creator_name: str,
        publisher_name: str,
        project_name: str = "DefaultProject",
        status: str = "Draft",
        version: str = "v001",
        publish_path: str = "N/A",
        preview_image_path: str = "N/A"
    ) -> Optional[str]:
        """
        Creates a new network node in Maya to store metadata for a new asset.

        Returns:
            Optional[str]: The name of the created network node if successful, None otherwise.
        """
        # Parameter validation
        for param, value in {
            'department': department,
            'asset_type': asset_type,
            'asset_name': asset_name,
            'creator_name': creator_name,
            'publisher_name': publisher_name
        }.items():
            if not value:
                mc.error(f"Parameter '{param}' is required and cannot be empty.")
                return None

        base_network_node_name = f"{asset_name}{AssetSceneUtils.METADATA_SUFFIX}"
        AssetSceneUtils.logger.info(f"Creating asset metadata node: {base_network_node_name}")

        existing_node = AssetSceneUtils.get_metadata_node_name()
        if existing_node:
            raise RuntimeError(f"A metadata node already exists in the scene: '{existing_node}'")

        try:
            network_node = mc.createNode("network", name=base_network_node_name)
            AssetSceneUtils.logger.info(f"Created network node: '{network_node}'")
        except RuntimeError as e:
            mc.error(f"Failed to create network node '{base_network_node_name}': {e}")
            return None

        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        attributes = {
            "asset_name": asset_name,
            "asset_type": asset_type,
            "department": department,
            "project_name": project_name,
            "status": status,
            "creator_name": creator_name,
            "publisher_name": publisher_name,
            "creation_date": current_date,
            "publish_date": current_date,
            "publish_path": publish_path,
            "preview_image_path": preview_image_path,
            "version": version,
            "maya_version": mc.about(version=True)
        }

        for attr, value in attributes.items():
            attr_name = attr.lower()
            if not mc.attributeQuery(attr_name, node=network_node, exists=True):
                mc.addAttr(network_node, longName=attr_name, dataType="string")
            mc.setAttr(f"{network_node}.{attr_name}", value, type="string")

        for attr in attributes.keys():
            mc.setAttr(f"{network_node}.{attr.lower()}", lock=True)
        mc.lockNode(network_node, lock=True)

        mc.select(network_node)
        AssetSceneUtils.logger.info(f"Network node '{network_node}' created with metadata.")
        return network_node

    @staticmethod
    def update_asset_metadata(updates: Dict[str, str]) -> bool:
        """
        Updates attributes on the asset metadata node.

        Args:
            updates (dict): Attribute-value pairs to update.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        node = AssetSceneUtils.get_metadata_node_name()
        if not node:
            AssetSceneUtils.logger.warning("No metadata node found to update.")
            return False

        is_locked = mc.lockNode(node, query=True, lock=True)[0]

        try:
            if is_locked:
                mc.lockNode(node, lock=False)

            for attr, value in updates.items():
                attr_name = f"{node}.{attr}"
                if mc.attributeQuery(attr, node=node, exists=True):
                    mc.setAttr(attr_name, lock=False)
                    mc.setAttr(attr_name, value, type="string")
                    mc.setAttr(attr_name, lock=True)
                else:
                    AssetSceneUtils.logger.warning(f"Attribute '{attr}' does not exist on '{node}'.")

            return True

        except Exception as e:
            mc.error(f"Failed to update metadata on '{node}': {e}")
            return False

        finally:
            if is_locked:
                mc.lockNode(node, lock=True)
