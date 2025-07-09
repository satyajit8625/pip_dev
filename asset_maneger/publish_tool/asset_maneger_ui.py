from PySide2 import QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as mc
import importlib
import tempfile
import os
import shutil  # 🔧 Required for copying preview images



# Import and reload utility modules
import project_config as config
import publish_tool.core.asset_scene_utils as asset_scene_utils_module
import publish_tool.core.user_utils as user_utils_module
import publish_tool.core.file_utils as file_utils_module
import publish_tool.core.version_utils as version_utils_module
import publish_tool.core.json_utils as json_utils_module


importlib.reload(asset_scene_utils_module)
importlib.reload(user_utils_module)
importlib.reload(file_utils_module)
importlib.reload(version_utils_module)
importlib.reload(json_utils_module)
importlib.reload(config)

def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class ClickableLabel(QtWidgets.QLabel):
    clicked = QtCore.Signal()
    def mousePressEvent(self, event):
        self.clicked.emit()

class CreateAssetDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(CreateAssetDialog, self).__init__(parent)
        self.setWindowTitle("Create New Asset")
        self.setFixedSize(300, 200)
        self.setStyleSheet("""
            QLabel { color: #e0e0e0; font-size: 10.5pt; }
            QLineEdit {
                background-color: #3B3B3B;
                padding: 6px;
                color: #e0e0e0;
                font-size: 10.5pt;
                border: none;
                border-radius: 0px;
            }
            QPushButton {
                background-color: #3a79c5;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #3366aa; }
        """)
        self.asset_name_input = QtWidgets.QLineEdit()
        self.asset_name_input.setPlaceholderText("Enter asset name")
        self.asset_type_dropdown = QtWidgets.QComboBox()
        self.asset_type_dropdown.addItems(["character", "prop", "vehicle", "environment", "other"])
        self.asset_type_dropdown.setMinimumHeight(32)
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("Asset Name:", self.asset_name_input)
        form_layout.addRow("Asset Type:", self.asset_type_dropdown)
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addStretch()
        layout.addWidget(button_box)

    def get_data(self):
        return self.asset_name_input.text().strip(), self.asset_type_dropdown.currentText()

class AssetPublisherUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AssetPublisherUI, self).__init__(parent)
        self.setWindowTitle("Asset Publisher")
        self.setMinimumWidth(520)
        self.setParent(parent)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.MSWindowsFixedSizeDialogHint)
        self.metadata_labels = {}
        self.preview_image_path = ""

        self.config = getattr(config, "CONFIG_DATA", {})
        self.project_name = self.config.get("project_name", "Unknown Project")
        self.project_root = self.config.get("project_path", "N/A")

        # Initialize logic class
        self.logic = AssetPublisherLogic(self.project_root, self.project_name)

        # Load initial metadata using logic class
        metadata = self.logic.load_asset_metadata()
        self.asset_name = metadata.get("asset_name", "Unnamed")
        self.asset_type = metadata.get("asset_type", "Unknown")
        self.version = metadata.get("version", "v001")
        self.creator = metadata.get("creator_name", "Unknown")

        if self.project_root != "N/A" and self.asset_name != "Unnamed" and self.asset_type != "Unknown":
            self.publish_dir = os.path.join(self.project_root, self.asset_type, self.asset_name, "publish").replace("\\", "/")
        else:
            self.publish_dir = metadata.get("publish_path", "N/A")

        self.setStyleSheet("""
            QWidget {
                background-color: #444444;
                color: #e0e0e0;
                font-family: 'Segoe UI', 'Arial';
                font-size: 10.5pt;
            }
            QLabel { color: #e0e0e0; font-size: 10.5pt; }
            QTextEdit, QLineEdit {
                background-color: #3B3B3B;
                border: none;
                border-radius: 0px;
                padding: 6px;
                color: #e0e0e0;
                font-size: 10.5pt;
            }
        """)
        self.build_ui()

    def build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        artist_name = os.environ.get("USERNAME") or os.environ.get("USER") or "JohnDoe"

        top_row = QtWidgets.QHBoxLayout()
        self.hamburger_btn = QtWidgets.QPushButton("\u22EE")
        self.hamburger_btn.setFixedWidth(30)
        self.hamburger_btn.setFlat(True)
        self.hamburger_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 28px;
                color: #e0e0e0;
            }
        """)
        self.hamburger_btn.clicked.connect(self.show_menu)
        self.project_label = QtWidgets.QLabel(f"Project Name: {self.project_name}")
        self.project_label.setAlignment(QtCore.Qt.AlignCenter)
        self.project_label.setStyleSheet("font-weight: bold; font-size: 11.5pt;")
        user_label = QtWidgets.QLabel(f"<b>User:</b> {artist_name}")
        user_label.setStyleSheet("color: #aaa; font-size: 10.5pt;")

        top_row.addWidget(self.hamburger_btn)
        top_row.addStretch()
        top_row.addWidget(self.project_label)
        top_row.addStretch()
        top_row.addWidget(user_label)
        main_layout.addLayout(top_row)

        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        main_layout.addWidget(separator)

        dept_row = QtWidgets.QHBoxLayout()
        dept_label = QtWidgets.QLabel("Department:")
        dept_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        self.department_dropdown = QtWidgets.QComboBox()
        self.department_dropdown.addItems(["modeling", "rigging", "texturing"])
        self.department_dropdown.setCurrentText("modeling")
        self.department_dropdown.setFixedHeight(34)
        self.department_dropdown.setMinimumWidth(480)
        self.department_dropdown.setStyleSheet("""
            QComboBox {
                background-color: #3B3B3B;
                color: #e0e0e0;
            }
        """)
        dept_row.addWidget(dept_label)
        dept_row.addWidget(self.department_dropdown)
        dept_row.addStretch()
        main_layout.addLayout(dept_row)

        comment_label = QtWidgets.QLabel("Publish Info:")
        comment_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        main_layout.addWidget(comment_label)

        comment_row = QtWidgets.QHBoxLayout()
        self.comment_box = QtWidgets.QTextEdit()
        self.comment_box.setPlaceholderText("Enter publish information or task details...")
        self.comment_box.setMinimumHeight(120)

        self.preview_label = ClickableLabel()
        self.preview_label.setFixedSize(320, 220)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 1px dashed #666;
                background-color: #3a3a3a;
                color: #888;
                font-style: italic;
                font-size: 10pt;
            }
        """)
        self.preview_label.setAlignment(QtCore.Qt.AlignCenter)
        self.preview_label.setText("Click to Capture")
        self.preview_label.setToolTip("Click to capture viewport preview.")
        self.preview_label.clicked.connect(lambda: self.logic.capture_viewport(self.preview_label)) # Connect to logic method and pass label

        preview_layout = QtWidgets.QVBoxLayout()
        preview_layout.setSpacing(8)
        preview_layout.addWidget(self.preview_label)

        info_fields = {
            "Asset Name": self.asset_name,
            "Asset Type": self.asset_type,
            "Version": self.version,
            "Artist": self.creator,
            "Publish Path": self.publish_dir
        }
        for key, value in info_fields.items():
            label = QtWidgets.QLabel(f"<b>{key}:</b> {value}")
            label.setStyleSheet("color: #bbb; font-size: 10.5pt;")
            if key == "Publish Path":
                label.setWordWrap(True)
            preview_layout.addWidget(label)
            self.metadata_labels[key] = label

        comment_row.addWidget(self.comment_box)
        comment_row.addLayout(preview_layout)
        main_layout.addLayout(comment_row)

        publish_btn = QtWidgets.QPushButton("Publish")
        publish_btn.setFixedSize(200, 46)
        publish_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a79c5;
                color: white;
                font-weight: bold;
                font-size: 11pt;
                border-radius: 6px;
                padding: 6px 20px;
            }
            QPushButton:hover {
                background-color: #3366aa;
            }
        """)
        publish_btn.clicked.connect(self.publish_asset_action) # Connect to UI action method
        main_layout.addSpacing(10)
        main_layout.addWidget(publish_btn, alignment=QtCore.Qt.AlignHCenter)

    def publish_asset_action(self):
        """Action method to trigger logic publish."""
        comment = self.comment_box.toPlainText().strip()
        department = self.department_dropdown.currentText().lower()
        self.logic.publish_asset(comment, department, self.metadata_labels, self.preview_label) # Pass UI data/elements

    def show_menu(self):
        menu = QtWidgets.QMenu(self)
        new_icon = self.style().standardIcon(QtWidgets.QStyle.SP_FileIcon)
        refresh_icon = self.style().standardIcon(QtWidgets.QStyle.SP_BrowserReload)
        close_icon = self.style().standardIcon(QtWidgets.QStyle.SP_DialogCloseButton)
        menu.addAction(new_icon, "Create New Asset", self.create_new_asset_action) # Connect to UI action method
        menu.addAction(refresh_icon, "Refresh Metadata", self.refresh_metadata_action) # Connect to UI action method
        menu.addSeparator()
        menu.addAction(close_icon, "Close", self.close)
        pos = self.hamburger_btn.mapToGlobal(QtCore.QPoint(0, self.hamburger_btn.height()))
        menu.exec_(pos)

    def create_new_asset_action(self):
        """Action method to trigger logic for creating new asset."""
        dialog = CreateAssetDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            asset_name, asset_type = dialog.get_data()
            if asset_name:
                QtWidgets.QMessageBox.information(self, "Asset Created", f"Asset Name: {asset_name}\nAsset Type: {asset_type}")
                self.logic.create_new_asset(asset_name, asset_type, self.department_dropdown.currentText().lower(), self.metadata_labels) # Pass UI data/elements
            else:
                QtWidgets.QMessageBox.warning(self, "Missing Name", "Please enter a valid asset name.")

    def refresh_metadata_action(self):
        """Action method to trigger logic for refreshing metadata."""
        self.logic.refresh_metadata(self.metadata_labels) # Pass UI element

class AssetPublisherLogic:
    def __init__(self, project_root, project_name):
        self.project_root = os.path.join(project_root, project_name) if project_root != "N/A" else "N/A"
        self.project_name = project_name
        self.asset_name = "Unnamed"
        self.asset_type = "Unknown"
        self.version = "v001"
        self.creator = "Unknown"
        self.publish_dir = "N/A"
        self.preview_image_path = ""

        # Load initial metadata
        metadata = self.load_asset_metadata()
        self.update_attributes_from_metadata(metadata)


    def update_attributes_from_metadata(self, metadata):
        """Updates logic attributes based on metadata."""
        self.asset_name = metadata.get("asset_name", "Unnamed")
        self.asset_type = metadata.get("asset_type", "Unknown")
        self.version = metadata.get("version", "v001")
        self.creator = metadata.get("creator_name", "Unknown")
        self.publish_dir = metadata.get("publish_path", "N/A")
        if self.project_root != "N/A" and self.asset_name != "Unnamed" and self.asset_type != "Unknown":
             self.publish_dir = os.path.join(self.project_root, self.asset_type, self.asset_name, "publish").replace("\\", "/")


    def get_internal_department(self, department_name):
        """
        Returns the internal short code for the selected department.
        """
        mapping = {
            "modeling": "mod",
            "rigging": "rig",
            "texturing": "tex"
        }
        return mapping.get(department_name.lower(), "mod")  # Default to 'mod'

    def capture_viewport(self, preview_label):
        """
        Temporary preview only; doesn't save to file system or create directories.
        Requires preview_label to update the UI.
        """
        if not self.asset_name or not self.asset_type or not self.creator:
            QtWidgets.QMessageBox.warning(None, "Missing Information", "Asset metadata is missing. Cannot capture preview.")
            return

        # Save a temporary preview in temp directory
        temp_path = os.path.join(tempfile.gettempdir(), f"{self.asset_name}_temp_preview.jpg").replace("\\", "/")
        self.save_preview_image(temp_path, preview_label)

    def save_preview_image(self, image_path, preview_label):
        """
        Saves a preview image using playblast to the specified path.
        Requires preview_label to update the UI.

        Args:
            image_path (str): Full file path to save the preview image.
            preview_label (QtWidgets.QLabel): The label to display the preview.
        """
        try:
            mc.playblast(
                completeFilename=image_path,
                format='image',
                width=400,
                height=300,
                showOrnaments=False,
                frame=mc.currentTime(q=True),
                viewer=False,
                offScreen=True,
                percent=100,
                compression="jpg"
            )
            self.preview_image_path = image_path
            pixmap = QtGui.QPixmap(image_path)
            scaled = pixmap.scaled(preview_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            preview_label.setPixmap(scaled)
            preview_label.setText("")
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Capture Failed", f"Viewport capture failed:\n{e}")

    def publish_asset(self, comment, department_name, metadata_labels, preview_label):
        """
        Safely publish asset. Aborts if metadata is invalid or any step fails.
        Requires comment, department_name, metadata_labels, and preview_label.
        """
        try:
            # Step 1: Validate basic fields
            department = self.get_internal_department(department_name)

            if not self.asset_name or not self.asset_type or not self.creator:
                raise ValueError("Missing asset metadata. Please refresh or create an asset.")

            if not comment:
                raise ValueError("Publish comment is required.")

            # ✅ Step 2: Strict metadata check from scene
            metadata = self.load_asset_metadata()
            if not metadata or metadata.get("asset_name", "") in ["", "Unnamed"]:
                raise RuntimeError("No valid metadata found in scene. Cannot publish.")

            # ✅ Step 3: Only now proceed with directory creation
            publish_paths = file_utils_module.DirectoryUtils.create_publish_dir_structure(
                project_root=self.project_root,
                asset_name=self.asset_name,
                department=department,
                asset_type=self.asset_type,
                format_type="ma"
            )
            if not publish_paths:
                raise RuntimeError("Failed to create publish directory.")
            file_publish_path, metadata_path, preview_image_path = publish_paths

            # Step 4: Get versioned filename
            full_publish_path, file_name, new_version_str = version_utils_module.VersionUtils.update_version(
                path=file_publish_path,
                base_name=self.asset_name,
                suffix=department,
                ext=".ma"
            )
            self.version = new_version_str

            # Step 5: Save Maya scene
            mc.file(rename=full_publish_path)
            mc.file(save=True, type="mayaAscii")

            # Step 6: Save preview image
            preview_name = f"{self.asset_name}_{department}_prv_{self.version}.jpg"
            preview_path = os.path.join(preview_image_path, preview_name).replace("\\", "/")
            self.save_preview_image(preview_path, preview_label) # Pass preview_label

            # Step 7: Update metadata
            asset_scene_utils_module.AssetSceneUtils.update_asset_metadata({
                "department": department,
                "publisher_name": user_utils_module.UserUtils.get_os_user(),
                "publish_date": asset_scene_utils_module.datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "publish_path": file_publish_path,
                "preview_image_path": self.preview_image_path,
                "version": self.version
            })

            # Step 8: Add history
            live_metadata = self.load_asset_metadata()
            if not live_metadata:
                raise RuntimeError("Could not read updated asset metadata.")

            history_entry = {
                "asset_name": live_metadata.get("asset_name", "N/A"),
                "asset_type": live_metadata.get("asset_type", "N/A"),
                "version": live_metadata.get("version", "N/A"),
                "department": department,
                "publisher": live_metadata.get("publisher_name", "N/A"),
                "publish_date": asset_scene_utils_module.datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "comment": comment,
                "file_path": full_publish_path,
                "preview_image": self.preview_image_path
            }

            json_utils_module.update_publish_history(
                path=metadata_path,
                file_name="metadata.json",
                new_entry=history_entry
            )

            self.refresh_metadata(metadata_labels) # Pass metadata_labels
            QtWidgets.QMessageBox.information(None, "Publish Success", f"✅ Published to {department} with comment:\n{comment}")

        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Publish Failed", f"❌ Publish failed:\n{str(e)}")

    def refresh_metadata(self, metadata_labels):
        """
        Refreshes metadata and updates UI labels.
        Requires metadata_labels to update the UI.
        """
        metadata = self.load_asset_metadata()
        self.update_attributes_from_metadata(metadata)
        updates = {
            "Asset Name": self.asset_name,
            "Asset Type": self.asset_type,
            "Version": self.version,
            "Artist": self.creator,
            "Publish Path": self.publish_dir
        }
        for key, value in updates.items():
            label = metadata_labels.get(key)
            if label:
                label.setText(f"<b>{key}:</b> {value}")

    def create_new_asset(self, asset_name, asset_type, department_name, metadata_labels):
        """
        Creates a new asset and updates metadata.
        Requires asset_name, asset_type, department_name, and metadata_labels.
        """
        try:
            asset_scene_utils_module.AssetSceneUtils.create_new_asset(
                department=department_name,
                asset_type=asset_type,
                asset_name=asset_name,
                creator_name=user_utils_module.UserUtils.get_os_user(),
                publisher_name=user_utils_module.UserUtils.get_os_user(),
                project_name=self.project_name
            )
            self.refresh_metadata(metadata_labels) # Pass metadata_labels
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Creation Failed", f"Failed to create new asset:\n{e}")


    def load_asset_metadata(self):
        """
        Loads asset metadata from the scene.
        """
        try:
            metadata = asset_scene_utils_module.AssetSceneUtils.get_asset_data()
            self.update_attributes_from_metadata(metadata)
            return metadata
        except Exception as e:
            print("Failed to load metadata:", e)
            return {}

def show_ui():
    for widget in QtWidgets.QApplication.allWidgets():
        if isinstance(widget, AssetPublisherUI):
            widget.close()
    ui = AssetPublisherUI(parent=get_maya_main_window())
    ui.show()

def show():
    show_ui()

