import sys
import os
import maya.utils

def setup_pip_dev():
    script_dir = None
    # Find the directory of the current script in sys.path
    for path in sys.path:
        script_path = os.path.join(path, "userSetup.py")
        if os.path.exists(script_path):
            script_dir = path
            break

    if script_dir:
        # Calculate root_path relative to the script_dir
        # Go up three levels from scripts to pip_dev (scripts -> pip_dev -> sources -> pip_dev root)
        root_path = os.path.abspath(os.path.join(script_dir, "../../../"))
        asset_maneger_path = os.path.join(root_path, "asset_maneger")

        if os.path.isdir(asset_maneger_path) and asset_maneger_path not in sys.path:
            sys.path.append(asset_maneger_path)
            print(f"[pip_dev] ✅ Added path: {asset_maneger_path}")
        else:
            print(f"[pip_dev] ❌ Could not add path: {asset_maneger_path}")

    else:
        print("[pip_dev] ❌ Could not determine userSetup.py directory in sys.path")


maya.utils.executeDeferred(setup_pip_dev)
