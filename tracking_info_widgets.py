from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QSplitter, QInputDialog, QScrollArea, QTreeWidget, QTreeWidgetItem, QAbstractItemView


class QTrackingInfoTreeWidget(QTreeWidget):
    def __init__(self, image_viewer, parent=None):
        super().__init__(parent)
        self.image_viewer = image_viewer
        self.setHeaderLabels(["name", "value"])
        self.setColumnWidth(0, 300)
        self.setColumnWidth(1, 100)
        self.itemClicked.connect(self.on_tracking_info_item_clicked)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_A and self.hasFocus():
            if self.image_viewer.annotation_button.text() == "Annotation":
                return
            item = self.currentItem()
            if item:
                track_id = item.data(1, Qt.UserRole)
                self.image_viewer.clip.add_filtered_label_by_track_id(track_id)
                self.image_viewer.print_screen()
        elif event.key() == Qt.Key_Delete and self.hasFocus():
            if self.image_viewer.annotation_button.text() == "Annotation":
                return
            item = self.currentItem()
            if item:
                track_id = item.data(1, Qt.UserRole)
                self.image_viewer.clip.delete_label_by_track_id(track_id)
                self.image_viewer.print_screen()
        else:
            super().keyPressEvent(event)

    def update_tracking_info(self):
        # 清空跟踪信息显示区域
        self.clear()

        # 遍历跟踪信息并添加到跟踪信息显示区域
        for track_info in self.image_viewer.clip.tracking_info:
            # 创建ID条目
            track_item = QTreeWidgetItem(self, [f"ID-{track_info['id']}"])
            track_item.setData(0, Qt.UserRole, track_info['start_frame']-1)
            track_item.setData(1, Qt.UserRole, track_info['id'])

            # 添加子条目
            start_frame_item = QTreeWidgetItem(track_item, ["Start Frame", f"{track_info['start_frame']}"])
            start_frame_item.setData(0, Qt.UserRole, track_info['start_frame']-1)
            end_frame_item = QTreeWidgetItem(track_item, ["End Frame", f"{track_info['end_frame']}"])
            end_frame_item.setData(0, Qt.UserRole, track_info['end_frame']-1)
            
            frame_count_item = QTreeWidgetItem(track_item, ["Frame Count", f"{track_info['frame_count']}"])
            avg_conf_item = QTreeWidgetItem(track_item, ["Average Confidence", f"{track_info['average_confidence']}"])
            avg_conf_item.setFlags(avg_conf_item.flags() | Qt.ItemIsEditable)

            if self.image_viewer.highlighted_track_id==track_info['id']:
                self.setCurrentItem(track_item)

        # 将QTreeWidget展开到一个层级
        # self.expandToDepth(0)

    def on_tracking_info_item_clicked(self, item, column):
        parent_item = item.parent()
        if parent_item is not None:
            track_id = int(parent_item.text(0).split('-')[-1].strip())
        else:
            track_id = int(item.text(0).split('-')[-1].strip())
        self.image_viewer.highlighted_track_id = track_id
        
        frame_index = item.data(0, Qt.UserRole)
        if frame_index is not None:
            self.image_viewer.set_current_index(frame_index)

class QFilterTrackingInfoTreeWidget(QTreeWidget):
    def __init__(self, image_viewer, parent=None):
        super().__init__(parent)
        self.image_viewer = image_viewer
        self.setHeaderLabels(["name", "value"])
        self.setColumnWidth(0, 300)
        self.setColumnWidth(1, 100)
        self.itemClicked.connect(self.on_filtered_tracking_info_item_clicked)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_D and self.hasFocus():
            item = self.currentItem()
            if item:
                track_id = item.data(1, Qt.UserRole)
                # self.image_viewer.clip.delete_label_by_track_id(track_id)
                self.image_viewer.clip.undo_filtered_label_by_track_id(track_id)
                self.image_viewer.print_screen()
        elif event.key() == Qt.Key_Delete and self.hasFocus():
            if self.image_viewer.annotation_button.text() == "Annotation":
                return
            item = self.currentItem()
            if item:
                track_id = item.data(1, Qt.UserRole)
                self.image_viewer.clip.delete_filtered_label_by_track_id(track_id)
                self.image_viewer.print_screen()
        else:
            super().keyPressEvent(event)

    def update_tracking_info(self):
        # 清空跟踪信息显示区域
        self.clear()

        # 遍历跟踪信息并添加到跟踪信息显示区域
        for track_info in self.image_viewer.clip.filtered_tracking_info:
            # 创建ID条目
            track_item = QTreeWidgetItem(self, [f"ID-{track_info['id']}"])
            track_item.setData(0, Qt.UserRole, track_info['start_frame']-1)
            track_item.setData(1, Qt.UserRole, track_info['id'])

            # 添加子条目
            start_frame_item = QTreeWidgetItem(track_item, ["Start Frame", f"{track_info['start_frame']}"])
            start_frame_item.setData(0, Qt.UserRole, track_info['start_frame']-1)
            end_frame_item = QTreeWidgetItem(track_item, ["End Frame", f"{track_info['end_frame']}"])
            end_frame_item.setData(0, Qt.UserRole, track_info['end_frame']-1)
            
            frame_count_item = QTreeWidgetItem(track_item, ["Frame Count", f"{track_info['frame_count']}"])
            avg_conf_item = QTreeWidgetItem(track_item, ["Average Confidence", f"{track_info['average_confidence']}"])
            avg_conf_item.setFlags(avg_conf_item.flags() | Qt.ItemIsEditable)

            if self.image_viewer.highlighted_track_id==track_info['id']:
                self.setCurrentItem(track_item)

        # 将QTreeWidget展开到一个层级
        # self.expandToDepth(0)

    def on_filtered_tracking_info_item_clicked(self, item, column):
        parent_item = item.parent()
        if parent_item is not None:
            track_id = int(parent_item.text(0).split('-')[-1].strip())
        else:
            track_id = int(item.text(0).split('-')[-1].strip())
        self.image_viewer.highlighted_track_id = track_id
        
        frame_index = item.data(0, Qt.UserRole)
        if frame_index is not None:
            self.image_viewer.set_current_index(frame_index)
