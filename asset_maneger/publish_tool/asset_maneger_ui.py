from PySide2 import QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import importlib
import tempfile
import os

# Import and reload utility modules
import asset_scene_utils as asset_scene_utils_module
import user_utils as user_utils_module

importlib.reload(asset_scene_utils_module)
importlib.reload(user_utils_module)

from asset_scene_utils import AssetSceneUtils
from user_utils import UserUtils

def get_maya_main_window():
    """Get the main Maya window as a QWidget."""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class ClickableLabel(QtWidgets.QLabel):
    """A QLabel subclass that emits a signal when clicked."""
    clicked = QtCore.Signal()

    def mousePressEvent(self, event):
        self.clicked.emit()


class CreateAssetDialog(QtWidgets.QDialog):
    """Dialog for creating a new asset with name and type input."""
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
        self.asset_type_dropdown.addItems(["Character", "Prop", "Vehicle", "Environment", "Other"])
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
        """Return the asset name and type from the dialog."""
        return self.asset_name_input.text().strip(), self.asset_type_dropdown.currentText()


class AssetPublisherUI(QtWidgets.QWidget):
    """Main UI class for the Asset Publisher tool in Maya."""
    def __init__(self, parent=None):
        super(AssetPublisherUI, self).__init__(parent)
        self.setWindowTitle("Asset Publisher")
        self.setMinimumWidth(520)
        self.setParent(parent)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.MSWindowsFixedSizeDialogHint)

        self.metadata_labels = {}
        self.preview_image_path = ""
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
        """Construct and layout all UI elements."""
        main_layout = QtWidgets.QVBoxLayout(self)

        scene_path = cmds.file(q=True, sn=True)
        scene_file = os.path.basename(scene_path)
        project_name = os.path.basename(os.path.dirname(scene_path))
        artist_name = os.environ.get("USERNAME") or os.environ.get("USER") or "JohnDoe"
        publish_path = os.path.join(os.path.dirname(scene_path), "publish")

        metadata = self.load_asset_metadata()
        asset_name = metadata.get("asset_name", os.path.splitext(scene_file)[0])
        asset_type = metadata.get("asset_type", "Unknown")
        version = metadata.get("version", "v001")
        creator = metadata.get("creator_name", artist_name)
        publish_dir = metadata.get("publish_path", publish_path)
        self.department = metadata.get("department", "Unknown")

        # Top bar
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

        self.project_label = QtWidgets.QLabel(f"Project: {project_name}")
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

        # Department row
        dept_row = QtWidgets.QHBoxLayout()
        dept_label = QtWidgets.QLabel("Department:")
        dept_label.setStyleSheet("font-weight: bold; font-size: 11pt;")

        self.department_dropdown = QtWidgets.QComboBox()
        self.department_dropdown.addItems(["Model", "Rig", "Animation", "Lookdev", "Layout", "FX"])
        self.department_dropdown.setCurrentText(self.department)
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

        # Publish Info
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
        self.preview_label.clicked.connect(self.capture_viewport)

        preview_layout = QtWidgets.QVBoxLayout()
        preview_layout.setSpacing(8)
        preview_layout.addWidget(self.preview_label)

        # Metadata labels
        info_fields = {
            "Asset Name": asset_name,
            "Asset Type": asset_type,
            "Version": version,
            "Artist": creator,
            "Publish Path": publish_dir
        }
        self.metadata_labels = {}
        for key, value in info_fields.items():
            label = QtWidgets.QLabel(f"<b>{key}:</b> {value}")
            label.setStyleSheet("color: #bbb; font-size: 10.5pt;")
            preview_layout.addWidget(label)
            self.metadata_labels[key] = label

        comment_row.addWidget(self.comment_box)
        comment_row.addLayout(preview_layout)
        main_layout.addLayout(comment_row)

        # Publish button
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
        publish_btn.clicked.connect(self.publish_asset)
        main_layout.addSpacing(10)
        main_layout.addWidget(publish_btn, alignment=QtCore.Qt.AlignHCenter)

    def show_menu(self):
        """Display the hamburger context menu."""
        menu = QtWidgets.QMenu(self)
        menu.addAction("Create New Asset", self.create_new_asset)
        menu.addAction("Refresh Metadata", self.refresh_metadata)
        menu.addAction("Close", self.close)
        pos = self.hamburger_btn.mapToGlobal(QtCore.QPoint(0, self.hamburger_btn.height()))
        menu.exec_(pos)

    def refresh_metadata(self):
        """Update only the metadata labels using latest scene data."""
        metadata = self.load_asset_metadata()
        updates = {
            "Asset Name": metadata.get("asset_name", "Unnamed"),
            "Asset Type": metadata.get("asset_type", "Unknown"),
            "Version": metadata.get("version", "v001"),
            "Artist": metadata.get("creator_name", "Unknown"),
            "Publish Path": metadata.get("publish_path", "N/A")
        }

        for key, value in updates.items():
            label = self.metadata_labels.get(key)
            if label:
                label.setText(f"<b>{key}:</b> {value}")

    def create_new_asset(self):
        """Open the Create Asset dialog and call the asset creation method."""
        dialog = CreateAssetDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            asset_name, asset_type = dialog.get_data()
            if asset_name:
                QtWidgets.QMessageBox.information(self, "Asset Created", f"Asset Name: {asset_name}\nAsset Type: {asset_type}")
                AssetSceneUtils.create_new_asset(
                    department=self.department_dropdown.currentText().lower(),
                    asset_type=asset_type,
                    asset_name=asset_name,
                    creator_name=UserUtils.get_os_user(),
                    publisher_name=UserUtils.get_os_user()
                )
                self.refresh_metadata()
            else:
                QtWidgets.QMessageBox.warning(self, "Missing Name", "Please enter a valid asset name.")

    def capture_viewport(self):
        """Capture the current Maya viewport to a temporary JPG and show it in the UI."""
        temp_dir = tempfile.gettempdir()
        image_path = os.path.join(temp_dir, "viewport_capture.jpg")
        cmds.playblast(
            completeFilename=image_path,
            format='image',
            width=400,
            height=300,
            showOrnaments=False,
            frame=cmds.currentTime(q=True),
            viewer=False,
            offScreen=True,
            percent=100,
            compression="jpg"
        )
        self.preview_image_path = image_path
        pixmap = QtGui.QPixmap(image_path)
        scaled = pixmap.scaled(self.preview_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.preview_label.setPixmap(scaled)
        self.preview_label.setText("")

    def publish_asset(self):
        """Handle the publish button click."""
        comment = self.comment_box.toPlainText().strip()
        selected_department = self.department_dropdown.currentText()
        if not comment:
            QtWidgets.QMessageBox.warning(self, "Missing Comment", "Please enter a publish comment.")
            return

        msg = f"Publishing to {selected_department} department with comment:\n{comment}"
        if self.preview_image_path:
            msg += f"\nPreview Image: {self.preview_image_path}"

        QtWidgets.QMessageBox.information(self, "Publish Asset", msg)

    def load_asset_metadata(self):
        """Load and return asset metadata from the scene."""
        try:
            return AssetSceneUtils.get_asset_data()
        except Exception as e:
            print("Failed to load metadata:", e)
            return {}

def show_ui():
    """Ensure only one instance of the UI is open at a time."""
    for widget in QtWidgets.QApplication.allWidgets():
        if isinstance(widget, AssetPublisherUI):
            widget.close()
    ui = AssetPublisherUI(parent=get_maya_main_window())
    ui.show()

def show():
    """Alias to show the UI."""
    show_ui()