"""# File: init_env.py

import sys
import os

# === Auto-detect the root project directory ===
CURRENT_FILE = os.path.abspath(__file__)
THIS_DIR = os.path.dirname(CURRENT_FILE)

# Assume init_env.py is inside something like E:/pip_dev or a subfolder
# Walk up until we hit 'pip_dev' or define it explicitly
def find_project_root(start_path, marker_folder="pip_dev"):
    while start_path and os.path.basename(start_path).lower() != marker_folder.lower():
        new_path = os.path.dirname(start_path)
        if new_path == start_path:
            break
        start_path = new_path
    return start_path if os.path.basename(start_path).lower() == marker_folder.lower() else None

PROJECT_ROOT = find_project_root(THIS_DIR) or r"E:\pip_dev"  # fallback default

# Define asset manager root
ASSET_MGR_ROOT = os.path.join(PROJECT_ROOT, "asset_maneger")

# === List of subdirectories to add to sys.path ===
SUBDIRS = [
    PROJECT_ROOT,
    ASSET_MGR_ROOT,
    os.path.join(ASSET_MGR_ROOT, "publish_tool"),
    os.path.join(ASSET_MGR_ROOT, "publish_tool", "core"),
    os.path.join(ASSET_MGR_ROOT, "publish_tool", "tools"),
    os.path.join(ASSET_MGR_ROOT, "publish_tool", "utils"),
    os.path.join(ASSET_MGR_ROOT, "publish_tool", "config"),  # optional
]

# === Add all valid paths to sys.path ===
for path in SUBDIRS:
    if os.path.exists(path) and path not in sys.path:
        sys.path.append(path)

# === Set global environment variables ===
os.environ["ASSET_PIPELINE_ROOT"] = PROJECT_ROOT
os.environ["ASSET_PIPELINE_ENV"] = "development"

# === Confirm setup ===
print("[AssetPipeline] ✅ Environment initialized.")
print("[AssetPipeline] 📁 Project Root:", PROJECT_ROOT)
print("[AssetPipeline] 🧩 sys.path entries:")
for p in SUBDIRS:
    print("  -", p)
"""