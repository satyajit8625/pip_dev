import sys
import os

# Set the root of your pipeline project
PROJECT_ROOT = r"E:\pip_dev\asset_maneger\publish_tool"

# Define subfolders you want to add to Python's sys.path
TOOLS_PATH = os.path.join(PROJECT_ROOT, "tools")
CORE_PATH = os.path.join(PROJECT_ROOT, "core")
UTILS_PATH = os.path.join(PROJECT_ROOT, "utils")

# Add each path to sys.path if not already present
for path in [PROJECT_ROOT,TOOLS_PATH, CORE_PATH, UTILS_PATH]:
    if path not in sys.path:
        sys.path.append(path)

# Optional: Set environment variable to access project root globally
os.environ["ASSET_PIPELINE_ROOT"] = PROJECT_ROOT

# Confirm setup
print("[AssetPipeline] Environment set. Root:", PROJECT_ROOT)
