import os
import json

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QSlider, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QMessageBox

from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QSplitter, QInputDialog, QScrollArea, QTreeWidget, QTreeWidgetItem, QAbstractItemView
# from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QDialog, QRadioButton, QButtonGroup, QTextEdit, QTabWidget, QLineEdit

from PyQt5.QtWidgets import QLabel, QRadioButton, QVBoxLayout, QPushButton, QDialog, QButtonGroup, QGridLayout

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene

class EditBBoxStateDialog(QDialog):
    def __init__(self, current_color, current_blink_state, parent=None):
        super().__init__(parent)
        color_names = ["red", "green", "yellow", "black", "uncertain"]
        blink_states = ["no_blink", "blink"]

        self.setWindowTitle("Edit BBox State")
        layout = QVBoxLayout()

        self.color_button_group = QButtonGroup(self)
        self.blink_state_button_group = QButtonGroup(self)

        # Color options
        color_label = QLabel("Color:")
        layout.addWidget(color_label)

        color_layout = QGridLayout()
        for index, color_name in enumerate(color_names):
            radio_button = QRadioButton(color_name)
            self.color_button_group.addButton(radio_button, index)
            color_layout.addWidget(radio_button, index // 4, index % 4)

            if color_name == current_color:
                radio_button.setChecked(True)

        layout.addLayout(color_layout)

        # Blink state options
        blink_state_label = QLabel("Blink state:")
        layout.addWidget(blink_state_label)

        blink_state_layout = QGridLayout()
        for index, blink_state in enumerate(blink_states):
            radio_button = QRadioButton(blink_state)
            self.blink_state_button_group.addButton(radio_button, index)
            blink_state_layout.addWidget(radio_button, index // 4, index % 4)

            if blink_state == current_blink_state:
                radio_button.setChecked(True)
            
        layout.addLayout(blink_state_layout)

        # OK button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

        self.setLayout(layout)

    def selected_color(self):
        if self.color_button_group.checkedButton():
            return self.color_button_group.checkedButton().text()
        else:
            return None

    def selected_blink_state(self):
        if self.blink_state_button_group.checkedButton():
            return self.blink_state_button_group.checkedButton().text()
        else:
            return None

class QBBoxesInfoTreeWidget(QTreeWidget):
    def __init__(self, image_viewer, parent=None):
        super().__init__(parent)
        self.image_viewer = image_viewer
        self.setHeaderLabels(["name", "value"])
        self.setColumnWidth(0, 300)
        self.setColumnWidth(1, 100)
        self.itemClicked.connect(self.on_bboxes_info_item_single_clicked)
        self.itemChanged.connect(self.on_bboxes_info_item_changed)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete and self.hasFocus():
            if self.image_viewer.annotation_button.text() == "Annotation":
                return
            item = self.currentItem()
            if item:
                bbox_id = item.data(1, Qt.UserRole)
                self.image_viewer.clip.delete_label_by_index(self.image_viewer.current_index, bbox_id, filtered=self.image_viewer.edit_filtered_track)
            self.image_viewer.print_screen()
        else:
            super().keyPressEvent(event)
        

    def update_bboxes_info(self):
        self.itemChanged.disconnect(self.on_bboxes_info_item_changed)
        # 清空跟踪信息显示区域
        self.clear()

        bboxes_info = self.image_viewer.clip.get_label_by_index(self.image_viewer.current_index, filtered=self.image_viewer.edit_filtered_track)
            
        # 遍历跟踪信息并添加到跟踪信息显示区域
        for bbox_info in bboxes_info.values():
            # 创建ID条目
            bbox_item = QTreeWidgetItem(self, [f"BboxID-{bbox_info.bbox_id}", ""])
            bbox_item.setData(0, Qt.UserRole, bbox_info.track_id)
            bbox_item.setData(1, Qt.UserRole, bbox_info.bbox_id)

            # 添加子条目
            color_item = QTreeWidgetItem(bbox_item, ["Confidence", f"{bbox_info.det_confidence:.3f}"])
            color_item.setData(0, Qt.UserRole, bbox_info.track_id)
            color_item = QTreeWidgetItem(bbox_item, ["Color", f"{bbox_info.color_name}"])
            color_item.setData(0, Qt.UserRole, bbox_info.track_id)
            color_item.setData(1, Qt.UserRole, bbox_info.bbox_id)
            blink_state_item = QTreeWidgetItem(bbox_item, ["Blink_state", f"{bbox_info.blink_state}"])
            blink_state_item.setData(0, Qt.UserRole, bbox_info.track_id)
            blink_state_item.setData(1, Qt.UserRole, bbox_info.bbox_id)
            track_id_item_label = QTreeWidgetItem(bbox_item, ["Track_id", f"{bbox_info.track_id}"])
            track_id_item_label.setData(0, Qt.UserRole, bbox_info.track_id)
            track_id_item_label.setData(1, Qt.UserRole, bbox_info.bbox_id)
            
            if self.image_viewer.highlighted_bbox_id==bbox_info.bbox_id:
                self.setCurrentItem(bbox_item)
                # self.setFocus()
                
        self.set_track_id_items_editable(self.image_viewer.set_bbox_items_editable)
        # 将QTreeWidget展开到一个层级
        self.expandToDepth(0)
        self.itemChanged.connect(self.on_bboxes_info_item_changed)

    def set_track_id_items_editable(self, editable):
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            track_id_item = item.child(3)
            if editable:
                track_id_item.setFlags(track_id_item.flags() | Qt.ItemIsEditable)
            else:
                track_id_item.setFlags(track_id_item.flags() & ~Qt.ItemIsEditable)

    def on_bboxes_info_item_single_clicked(self, item, column):
        parent = item.parent()
        if parent:
            indexOfChild = parent.indexOfChild(item)
        else:
            indexOfChild = -1
            
        track_id = item.data(0, Qt.UserRole)
        bbox_id = item.data(1, Qt.UserRole)
        if track_id is not None:
            self.image_viewer.highlighted_track_id = track_id
            self.image_viewer.highlighted_bbox_id = bbox_id
        
        if indexOfChild==-1:
            self.image_viewer.print_screen()
        
        # Annotation Edit
        if self.image_viewer.annotation_button.text() == "Annotation": # visualizing
            return

        if parent and (indexOfChild == 1 or indexOfChild == 2):
            current_color = parent.child(1).text(1)  # Assuming "Color" is the 2nd child
            current_blink_state = parent.child(2).text(1)  # Assuming "Blink_state" is the 3rd child

            dialog = EditBBoxStateDialog(current_color, current_blink_state, self.image_viewer)
            if dialog.exec_() == QDialog.Accepted:
                new_color = dialog.selected_color()
                new_blink_state = dialog.selected_blink_state()
                self.image_viewer.clip.set_label_color_blink_state_by_index(self.image_viewer.current_index, bbox_id, new_color, new_blink_state, filtered=self.image_viewer.edit_filtered_track)
                
                self.image_viewer.print_screen()
                return
        
    def on_bboxes_info_item_changed(self, item, column):
        if self.image_viewer.annotation_button.text() == "Annotation":
            return

        parent = item.parent()
        if parent and parent.indexOfChild(item) == 3:  # Assuming "Track_id" is the 5th child
            previous_track_id = parent.data(0, Qt.UserRole)
            edit_bbox_id = parent.data(1, Qt.UserRole)
            if not item.text(1).isdigit():
                # If the input is not a positive integer, show an error message and revert the change
                QMessageBox.critical(None, "Error", "Input must be a positive integer.")
                item.setText(1, f"{previous_track_id}")
                return
            
            new_track_id = int(item.text(1))  # 从文本中提取 track id
            
            self.image_viewer.clip.switch_label_track_id_last_frames(self.image_viewer.current_index, previous_track_id, new_track_id, filtered=self.image_viewer.edit_filtered_track)
            self.image_viewer.print_screen()