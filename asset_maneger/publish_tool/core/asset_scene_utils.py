# File: asset_manager/publish_tool/core/asset_scene_utils.py

import maya.cmds as mc
import datetime

class AssetSceneUtils:
    """
    Utility class for asset-related scene operations in Maya.

    Provides methods for creating metadata nodes and retrieving asset data.
    """

    @staticmethod
    def get_asset_data():
        """
        Retrieves metadata from the only metadata node in the Maya scene.

        The metadata node must:
        - Be of type 'network'
        - Have a name ending with '_metadata_node'

        Returns:
            dict: Dictionary containing user-defined attribute names and their values.

        Raises:
            RuntimeError: If no metadata node or more than one metadata node is found.
        """
        asset_data = {}

        # Find all network nodes ending with '_metadata_node'
        metadata_nodes = [node for node in mc.ls(type='network') if node.endswith('_metadata_node')]

        if not metadata_nodes:
            raise RuntimeError("No metadata node found in the scene.")

        if len(metadata_nodes) > 1:
            print("this is line")
            mc.warning(f"Multiple metadata nodes found in the scene: {metadata_nodes}")

        asset_node = metadata_nodes[0]
        user_attrs = mc.listAttr(asset_node, userDefined=True) or []

        for attr in user_attrs:
            try:
                asset_data[attr] = mc.getAttr(f"{asset_node}.{attr}")
            except RuntimeError as e:
                mc.warning(f"Could not retrieve attribute '{attr}' from '{asset_node}': {e}")

        return asset_data

    @staticmethod
    def create_new_asset(department, asset_type, asset_name, creator_name, publisher_name):
        """
        Creates a new network node in Maya to store metadata for a new asset.

        This function generates a unique network node and populates it with
        essential asset information, including identification, personnel,
        dates, and publishing details.

        Args:
            department (str): Department responsible (e.g., "Modeling", "Rigging").
            asset_type (str): Asset type (e.g., "Prop", "Character", "Environment").
            asset_name (str): Unique asset name.
            creator_name (str): Creator of the asset.
            publisher_name (str): Publisher of the asset.

        Returns:
            str: The name of the created network node if successful, None otherwise.

        Raises:
            RuntimeError: If any metadata node already exists in the scene.
        """
        base_network_node_name = f"{asset_name}_metadata_node"
        print(f"{asset_name} is being created...")

        # === Check if any metadata node already exists ===
        existing_metadata_nodes = [node for node in mc.ls(type='network') if node.endswith('_metadata_node')]
        if existing_metadata_nodes:
            raise RuntimeError(f"A metadata node already exists in the scene: '{existing_metadata_nodes[0]}'")

        try:
            network_node = mc.createNode("network", name=base_network_node_name)
            print(f"Created network node: '{network_node}'")
        except RuntimeError as e:
            mc.error(f"Failed to create network node '{base_network_node_name}': {e}")
            return None

        # Generate attribute values
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        version = "v001"
        publish_path = "N/A"

        attributes = {
            "asset_name": asset_name,
            "asset_type": asset_type,
            "department": department,
            "project_name": "DefaultProject",
            "status": "Draft",
            "creator_name": creator_name,
            "publisher_name": publisher_name,
            "creation_date": current_date,
            "publish_date": current_date,
            "publish_path": publish_path,
            "version": version,
        }

        # Add and set attributes
        for attr, value in attributes.items():
            attr_name = attr.lower()
            if not mc.attributeQuery(attr_name, node=network_node, exists=True):
                mc.addAttr(network_node, longName=attr_name, dataType="string")
            mc.setAttr(f"{network_node}.{attr_name}", value, type="string")

        # Lock attributes and node
        for attr in attributes.keys():
            mc.setAttr(f"{network_node}.{attr.lower()}", lock=True)
        mc.lockNode(network_node, lock=True)

        # Select node
        mc.select(network_node)
        print(f"Network node '{network_node}' created with metadata.")

        return network_node
