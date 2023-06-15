import os
import json

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QBrush
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QSlider, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QMessageBox, QGroupBox, QSizePolicy

from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QSplitter, QInputDialog, QScrollArea, QTreeWidget, QTreeWidgetItem, QAbstractItemView
# from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QDialog, QRadioButton, QButtonGroup, QTextEdit, QTabWidget, QLineEdit

from PyQt5.QtWidgets import QLabel, QRadioButton, QVBoxLayout, QPushButton, QDialog, QButtonGroup, QGridLayout

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene

from tracking_info_widgets import QTrackingInfoTreeWidget, QFilterTrackingInfoTreeWidget
from bboxes_info_widgets import QBBoxesInfoTreeWidget, EditBBoxStateDialog

from module import CLIP, BBOX


class CustomSlider(QSlider):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_Up:
            self.setValue(self.value() - self.singleStep())
        elif key == Qt.Key_Down:
            self.setValue(self.value() + self.singleStep())
        else:
            super().keyPressEvent(event)

def get_color_by_id(label_id):
    # 使用HSV颜色空间，更容易区分颜色
    hue = int((120 + 45 * (label_id % 8)) % 360)
    saturation = 255
    value = 255
    return QColor.fromHsv(hue, saturation, value)

class CustomQLabel(QLabel):
    def __init__(self, image_viewer, parent=None):
        super().__init__(parent)
        self.image_viewer = image_viewer

    def mouseMoveEvent(self, event):
        pos = event.pos()
        x, y = pos.x(), pos.y()
        
        x_ratio, y_ratio = self.image_viewer.get_scale_ratio()
        original_x = int(x / x_ratio)
        original_y = int(y / y_ratio)
        
        self.image_viewer.coord_label.setText("x: {}, y: {}".format(original_x, original_y))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            if self.image_viewer.annotation_button.text() == "Annotation":
                return
            item = self.image_viewer.bboxes_info_area.currentItem()
            if item:
                bbox_id = item.data(1, Qt.UserRole)
                self.image_viewer.clip.delete_label_by_index(self.image_viewer.current_index, bbox_id, filtered=self.image_viewer.edit_filtered_track)
            self.image_viewer.print_screen()
        elif event.key() == Qt.Key_D:
            print('D key pressed')
        else:
            super().keyPressEvent(event)

class ImageViewer(QWidget):
    def __init__(self, clip_dir):
        super().__init__()
        self.clip_dir = clip_dir
        self.clip = CLIP(clip_dir)

        # 获取图片文件列表
        self.image_paths = self.clip.get_all_image_paths()
        self.show_bbox_color = True
        self.show_bbox_blink_state = True

        # 初始化界面
        self.init_ui()

        # 初始化定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_image)
        self.timer.start(50)  # 定时默认间隔50ms，20Hz

    def init_ui(self):
        # 设置窗口标题和大小
        self.setWindowTitle("Image Viewer")
        self.setGeometry(100, 100, 800, 600)

        # 在image_label之前添加一个新的标签用于显示坐标
        self.coord_label = QLabel(self)
        self.coord_label.setAlignment(Qt.AlignLeft)

        # 创建显示图片的标签
        #self.image_label = QLabel(self)
        self.image_label = CustomQLabel(self, self)
        # self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # self.image_label.setMinimumSize(400, 400)
        self.image_label.setMaximumSize(1920, 1080)
        # self.image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.image_label.mousePressEvent = self.image_label_clicked
        self.image_label.mouseDoubleClickEvent = self.image_label_double_clicked
        self.image_label.setMouseTracking(True)
        self.image_label.setFocusPolicy(Qt.StrongFocus)

        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)  # 设置为可调整大小

        # 创建滑块
        self.slider = CustomSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.image_paths) - 1)

        # 创建控制按钮
        self.play_button = QPushButton('Play', self)

        # 创建水平布局，并添加滑块和控制按钮
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.slider)
        control_layout.addWidget(self.play_button)

        self.show_bbox = QCheckBox('Show BBox', self)
        self.show_bbox.setChecked(True)
        self.show_bbox.stateChanged.connect(self.on_show_bbox_state_changed)
        self.show_bbox.stateChanged.connect(self.print_screen)
        
        self.show_filtered_bbox = QCheckBox('Show Filtered BBox', self)
        self.show_filtered_bbox.stateChanged.connect(self.on_show_filtered_bbox_state_changed)
        self.show_filtered_bbox.stateChanged.connect(self.print_screen)
        
        self.show_track = QCheckBox('Show Track', self)
        self.show_track.setChecked(True)
        self.show_track.stateChanged.connect(self.on_show_track_state_changed)
        self.show_track.stateChanged.connect(self.print_screen)

        self.show_filtered_track = QCheckBox('Show Filtered Track', self)
        self.show_filtered_track.stateChanged.connect(self.on_show_filtered_track_state_changed)
        self.show_filtered_track.stateChanged.connect(self.print_screen)

        # 创建垂直布局，并添加图片标签和控制布局
        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        layout.addWidget(self.coord_label)
        layout.addLayout(control_layout)

        # 创建一个包含图片路径的列表窗口
        self.image_list = QListWidget()
        # 添加图片到 image_list
        for img_path in self.image_paths:
            item = QListWidgetItem(img_path)
            self.image_list.addItem(item)

        # 添加跟踪信息显示区域
        self.tracking_info_area = QTrackingInfoTreeWidget(self, self)
        self.filtered_tracking_info_area = QFilterTrackingInfoTreeWidget(self)
        self.filtered_tracking_info_area.setHeaderHidden(True)

        # 添加bboxes信息显示区域
        self.bboxes_info_area = QBBoxesInfoTreeWidget(self, self)
        self.bboxes_info_area.setHeaderHidden(True)

        # 创建选项卡
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.West)

        # 创建 Basic 选项卡
        basic_tab = QWidget()
        basic_layout = QVBoxLayout()

        # 添加 Annotation 按钮
        self.annotation_button = QPushButton("Annotation", self)
        self.annotation_button.clicked.connect(self.toggle_annotation_button)
        basic_layout.addWidget(self.annotation_button)

        # 创建两个QGroupBox，一个用于常规复选框，一个用于过滤复选框
        regular_group = QGroupBox()
        filtered_group = QGroupBox()

        # 创建两个垂直布局，分别添加到QGroupBox中
        regular_checkbox_layout = QVBoxLayout(regular_group)
        filtered_checkbox_layout = QVBoxLayout(filtered_group)

        # 添加 show_bbox 和 show_track 到常规复选框布局
        regular_checkbox_layout.addWidget(self.show_bbox)
        regular_checkbox_layout.addWidget(self.show_track)

        # 添加 show_filtered_bbox 和 show_filtered_track 到过滤复选框布局
        filtered_checkbox_layout.addWidget(self.show_filtered_bbox)
        filtered_checkbox_layout.addWidget(self.show_filtered_track)

        # 设置QGroupBox的最大宽度
        regular_group.setMaximumWidth(250)  # 你可以调整这个数字
        filtered_group.setMaximumWidth(250)  # 你可以调整这个数字

        # 修改尺寸策略
        regular_group.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        filtered_group.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # 将checkbox_layout添加到基本布局中
        basic_layout.addWidget(regular_group)
        basic_layout.addWidget(filtered_group)

        # 添加 image_list
        basic_layout.addWidget(self.image_list)

        basic_tab.setLayout(basic_layout)

        self.tab_widget.addTab(basic_tab, "Basic")

        # 创建 Tracking Info 选项卡
        tracking_info_tab = QWidget()
        tracking_info_layout = QVBoxLayout()
        tracking_info_layout.addWidget(self.tracking_info_area)
        tracking_info_layout.addWidget(self.filtered_tracking_info_area)
        
        tracking_info_tab.setLayout(tracking_info_layout)
        self.tab_widget.addTab(tracking_info_tab, "Tracking Info")
        
        # 创建 Bboxes Info 选项卡
        bboxes_tab = QWidget()
        bboxes_layout = QVBoxLayout()
        bboxes_layout.addWidget(self.bboxes_info_area)
        bboxes_tab.setLayout(bboxes_layout)
        self.tab_widget.addTab(bboxes_tab, "Bboxes Info")
        
        # 创建 Operation 选项卡
        operation_tab = QWidget()
        operation_layout = QGridLayout()
        self.input_widgets = {}
        labels = ["match_thresh", "det_thresh", "track_thresh", "fuse_det_score", "max_distance", "track_buffer", "frame_rate"]
        default_values = ["0.99", "0.3", "0.3", "True", "100", "4", "30"]
        for i, (label, default_value) in enumerate(zip(labels, default_values)):
            label_widget = QLabel(label)
            if default_value.lower() == "true" or default_value.lower() == "false":
                input_widget = QCheckBox()
                input_widget.setChecked(default_value.lower() == "true")
            else:
                input_widget = QLineEdit(default_value)
            self.input_widgets[label] = input_widget  # 将输入部件添加到字典中
            operation_layout.addWidget(label_widget, i, 0)
            operation_layout.addWidget(input_widget, i, 1)
            
        # 添加 Run Tracker 按钮
        run_tracker_button = QPushButton("Run Tracker")
        run_tracker_button.clicked.connect(self.run_tracker_and_print_screen)
        operation_layout.addWidget(run_tracker_button, len(self.input_widgets), 0, 1, 2)

        # 添加 Run Blink 按钮
        run_blinker_button = QPushButton("Run Blinker")
        run_blinker_button.clicked.connect(self.run_blinker_and_print_screen)
        operation_layout.addWidget(run_blinker_button, len(self.input_widgets)+1, 0, 1, 2)
        
        # 添加 Run Hot Sequence Labeler 按钮
        self.input_widgets_labeler = {}
        labels = ["filtered_thresh"]
        default_values = ["0.94"]
        for i, (label, default_value) in enumerate(zip(labels, default_values)):
            label_widget = QLabel(label)
            if default_value.lower() == "true" or default_value.lower() == "false":
                input_widget = QCheckBox()
                input_widget.setChecked(default_value.lower() == "true")
            else:
                input_widget = QLineEdit(default_value)
            self.input_widgets_labeler[label] = input_widget  # 将输入部件添加到字典中
            operation_layout.addWidget(label_widget, len(self.input_widgets)+2+i, 0)
            operation_layout.addWidget(input_widget, len(self.input_widgets)+2+i, 1)
        
        run_hot_sequence_labeler_button = QPushButton("Run Hot Sequence Labeler")
        run_hot_sequence_labeler_button.clicked.connect(self.run_hot_sequence_labeler_and_print_screen)
        operation_layout.addWidget(run_hot_sequence_labeler_button, len(self.input_widgets)+len(self.input_widgets_labeler)+2, 0, 1, 2)
       
        run_export_label_button = QPushButton("Run Export Label")
        run_export_label_button.clicked.connect(self.run_export_label)
        operation_layout.addWidget(run_export_label_button, len(self.input_widgets)+len(self.input_widgets_labeler)+3, 0, 1, 2)
        
        # 信息显示栏目
        self.info_text_edit = QTextEdit()
        self.info_text_edit.setReadOnly(True)
        operation_layout.addWidget(self.info_text_edit, len(self.input_widgets)+len(self.input_widgets_labeler)+4, 0, 1, 2)
        
        operation_tab.setLayout(operation_layout)
        self.tab_widget.addTab(operation_tab, "Operation")

        # 将图片列表和跟踪信息显示区域放入一个垂直布局
        left_side_layout = QVBoxLayout()
        left_side_layout.addWidget(self.tab_widget)

        # 使用QSplitter将图片列表和跟踪信息显示区域的布局与现有布局分开
        splitter = QSplitter(Qt.Horizontal)
        left_side_widget = QWidget()
        left_side_widget.setLayout(left_side_layout)
        splitter.addWidget(left_side_widget)

        main_widget = QWidget()
        main_widget.setLayout(layout)
        splitter.addWidget(main_widget)

        # 设置初始窗口部件宽度
        splitter.setSizes([100, 800])

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(splitter)

        # 为控件添加事件处理函数
        self.slider.valueChanged.connect(self.set_current_index)
        self.play_button.clicked.connect(self.toggle_play)
        self.image_list.currentRowChanged.connect(self.set_current_index)
        
        # 设置初始状态
        self.current_index = 0
        self.highlighted_track_id = None
        self.highlighted_bbox_id = None
        self.set_bbox_items_editable = False
        self.edit_filtered_track = False
        self.playing = False
        # self.tracking_info_area.update_tracking_info()  # 在初始化UI时调用更新跟踪信息的方法
        # self.bboxes_info_area.update_bboxes_info()
        self.print_screen()

    def on_show_bbox_state_changed(self, state):
        if state == Qt.Checked:
            self.show_filtered_bbox.setChecked(False)
            self.show_filtered_track.setChecked(False)
            self.edit_filtered_track = False
    
    def on_show_filtered_bbox_state_changed(self, state):
        if state == Qt.Checked:
            self.show_bbox.setChecked(False)
            self.show_track.setChecked(False)
            self.edit_filtered_track = True

    def on_show_track_state_changed(self, state):
        if state == Qt.Checked:
            self.show_filtered_bbox.setChecked(False)
            self.show_filtered_track.setChecked(False)
            self.edit_filtered_track = False

    def on_show_filtered_track_state_changed(self, state):
        if state == Qt.Checked:
            self.show_bbox.setChecked(False)
            self.show_track.setChecked(False)
            self.edit_filtered_track = True

    def image_label_clicked(self, event):
        x, y = event.pos().x(), event.pos().y()
        bbox_id, track_id = self.select_bbox(x, y)
        if bbox_id:
            self.highlighted_bbox_id = bbox_id
        else:
            self.highlighted_bbox_id = None
        if track_id:
            self.highlighted_track_id = track_id
        self.print_screen()

    # def edit_bbox_state(self):
        

    def image_label_double_clicked(self, event):
        if self.annotation_button.text() == "Annotation":
            return
        x, y = event.pos().x(), event.pos().y()
        bbox_id, track_id = self.select_bbox(x, y)
        if bbox_id:
            for i in range(self.bboxes_info_area.topLevelItemCount()):
                bbox_item = self.bboxes_info_area.topLevelItem(i)
                if bbox_item.data(1, Qt.UserRole)==bbox_id:
                    current_color = bbox_item.child(1).text(1)  # Assuming "Color" is the 2nd child
                    current_blink_state = bbox_item.child(2).text(1)  # Assuming "Blink_state" is the 3rd child

                    dialog = EditBBoxStateDialog(current_color, current_blink_state, self)
                    if dialog.exec_() == QDialog.Accepted:
                        new_color = dialog.selected_color()
                        new_blink_state = dialog.selected_blink_state()
                        self.clip.set_label_color_blink_state_by_index(self.current_index, bbox_id, new_color, new_blink_state, filtered=self.edit_filtered_track)
                
            self.print_screen()

    def get_scale_ratio(self):
        pixmap_size = self.image_label.pixmap().size()
        label_size = self.image_label.size()
        x_ratio, y_ratio = label_size.width() / pixmap_size.width(), label_size.height() / pixmap_size.height()
        return (x_ratio, y_ratio)

    def select_bbox(self, x, y):
        x_ratio, y_ratio = self.get_scale_ratio()
        original_x = int(x / x_ratio)
        original_y = int(y / y_ratio)
        
        # 读取对应帧的标签文件
        bboxes = self.clip.get_label_by_index(self.current_index, filtered=self.edit_filtered_track)
        for bbox in bboxes.values():
            # 绘制 bounding box
            x1, y1, x2, y2 = bbox.ltrb
            if x1 <= original_x <= x2 and y1 <= original_y <= y2:
                for i in range(self.bboxes_info_area.topLevelItemCount()):
                    item = self.bboxes_info_area.topLevelItem(i)
                    # item_track_id = item.data(0, Qt.UserRole)
                    item_bbox_id = item.data(1, Qt.UserRole)

                    # 如果找到与所选 bbox 的 track_id 匹配的项目
                    if item_bbox_id == bbox.bbox_id:
                        return bbox.bbox_id, bbox.track_id
        return None, None

    def set_current_index(self, value):
        self.current_index = value
        self.image_list.setCurrentRow(self.current_index)  # 高亮当前图片地址条目
        self.slider.setValue(self.current_index) # 滑块跟随移动
        self.print_screen()

    def toggle_play(self):
        self.playing = not self.playing
        if self.playing:
            self.play_button.setText('Pause')
            self.timer.start(10)
        else:
            self.play_button.setText('Play')
            self.timer.stop()

    def update_image(self):
        if self.playing:
            self.current_index += 1
            if self.current_index >= len(self.image_paths):
                self.current_index = 0
                self.playing = False
            self.print_screen()
            self.slider.setValue(self.current_index)
        else:
            self.play_button.setText('Play')

    def print_image(self):
        image_path = self.image_paths[self.current_index]
        image = QPixmap(image_path)
        self.image_label.setPixmap(image)
        # scaled_image = image.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # self.image_label.setPixmap(scaled_image)
    
    def paint_bbox(self, paint_filtered=False):
        painter = QPainter(self.image_label.pixmap())
        
        # 读取对应帧的标签文件
        if not paint_filtered:
            bboxes = self.clip.get_label_by_index(self.current_index)
        else:
            bboxes = self.clip.get_filtered_label_by_index(self.current_index)
            
        for bbox in bboxes.values():
            # 绘制 bounding box
            x1, y1, x2, y2 = bbox.ltrb
            color_name = bbox.color_name
            
            pen_size = max(1, min(x2 - x1, y2 - y1) // 5)  # 设置画笔的粗细，最小为1，最大为bounding box宽高中的较小值的1/50
            if self.show_bbox_color:
                color = CLIP.color_name2color(color_name)
            else:
                color = (255, 0, 0, 255)
                
            pen = QPen(QColor(*color), pen_size)  # 设置画笔颜色和粗细
            painter.setPen(pen)
            painter.setBrush(QBrush(Qt.NoBrush))
            painter.drawRect(x1, y1, x2 - x1, y2 - y1)
            
            if self.show_bbox_blink_state:
                if bbox.blink_state=="blink":
                    # 绘制blink圆形
                    radius = (x2 - x1) // 2.5
                    painter.setPen(QPen(Qt.NoPen))
                    painter.setBrush(QBrush(QColor(255, 165, 0, 255)))
                    if y1 - radius*2 > radius:
                        painter.drawEllipse((x1 + x2) // 2 - radius, y1 - radius*3, radius * 2, radius * 2)
                    else:
                        painter.drawEllipse((x1 + x2) // 2 - radius, y2 + radius*3, radius * 2, radius * 2)
        painter.end()

    def paint_track(self, paint_filtered=False):
        painter = QPainter(self.image_label.pixmap())
        # 读取对应帧的标签文件
        if not paint_filtered:
            bboxes = self.clip.get_label_by_index(self.current_index)
        else:
            bboxes = self.clip.get_filtered_label_by_index(self.current_index)
            
        for bbox in bboxes.values():
            # 绘制 bounding box
            x1, y1, x2, y2 = bbox.ltrb
            track_id = bbox.track_id
            bbox_id = bbox.bbox_id
            if track_id==None or track_id==-1:
                continue
            color = get_color_by_id(track_id)

            # 适当扩大bounding box绘画的范围，这里扩大了10%的宽和高
            x1 -= (x2 - x1) * 0.1
            y1 -= (y2 - y1) * 0.1
            x2 += (x2 - x1) * 0.1
            y2 += (y2 - y1) * 0.1

            pen_size = max(1, min(x2 - x1, y2 - y1) // 10)  # 设置画笔的粗细，最小为1，最大为bounding box宽高中的较小值的1/50
            pen = QPen(color, pen_size)  # 设置画笔颜色和粗细
            painter.setPen(pen)
            painter.drawRect(x1, y1, x2 - x1, y2 - y1)
            
            # 绘制带底色的ID文本
            font_size = max(pen_size * 2, 10)  # 设定字体大小的最小值为10
            font = painter.font()
            font.setPointSize(font_size)
            painter.setFont(font)
            painter.setPen(QPen(Qt.NoPen))
            painter.setBrush(QBrush(color))
            text_rect = QRectF(x1, y2, font_size * len(str(track_id)), font_size * 1.5)
            painter.fillRect(text_rect, color)
            painter.setPen(QPen(Qt.black, 1))
            painter.drawText(text_rect, Qt.AlignCenter, str(track_id))
            
            if self.highlighted_track_id == track_id:
                painter.setPen(QPen(Qt.white, 2))  # 设置白色边框，线宽为2
                painter.setBrush(QBrush(Qt.NoBrush))
                painter.drawRect(text_rect)
            
            painter.setPen(QPen(Qt.NoPen))
            painter.setBrush(QBrush(Qt.NoBrush))

        painter.end()

    def print_screen(self):
        self.print_image()
        self.bboxes_info_area.update_bboxes_info()
        self.tracking_info_area.update_tracking_info()
        self.filtered_tracking_info_area.update_tracking_info()
        
        # 绘制 bounding box
        if self.show_bbox.isChecked():
            self.paint_bbox()

        if self.show_track.isChecked():
            self.paint_track()
        
        if self.show_filtered_bbox.isChecked():
            self.paint_bbox(paint_filtered=True)
        
        if self.show_filtered_track.isChecked():
            self.paint_track(paint_filtered=True)

    def run_tracker_and_print_screen(self):
        configs = dict()
        # 从输入部件中获取输入值并将其转换为适当的类型
        configs['match_thresh'] = float(self.input_widgets["match_thresh"].text())
        configs['det_thresh'] = float(self.input_widgets["det_thresh"].text())
        configs['track_thresh'] = float(self.input_widgets["track_thresh"].text())
        configs['fuse_det_score'] = self.input_widgets["fuse_det_score"].isChecked()
        configs['max_distance'] = int(self.input_widgets["max_distance"].text())
        configs['track_buffer'] = int(self.input_widgets["track_buffer"].text())
        configs['frame_rate'] = int(self.input_widgets["frame_rate"].text())

        # 将输入值传递给 run_tracker 函数
        self.clip.run_tracker(configs)
        self.info_text_edit.append("Run Tracker: Success!\n")
        # self.tracking_info_area.update_tracking_info()
        self.print_screen()

    def run_blinker_and_print_screen(self):
        self.clip.run_blinker()
        self.info_text_edit.append("Run Blinker: Success!\n")
        self.print_screen()

    def run_hot_sequence_labeler_and_print_screen(self):
        filtered_thresh = float(self.input_widgets_labeler["filtered_thresh"].text())
        for track_info in self.clip.filtered_tracking_info:
            self.clip.undo_filtered_label_by_track_id(track_info['id'])
        for track_info in self.clip.tracking_info:
            if track_info['average_confidence']>=filtered_thresh:
                self.clip.add_filtered_label_by_track_id(track_info['id'])
        self.info_text_edit.append("Run Hot Squence Labeler: Success!\n")
        self.print_screen()

    def run_export_label(self):
        self.clip.export_filtered_annos()
        self.info_text_edit.append("Write filtered labels: Success!\n")

    def toggle_annotation_button(self):
        if self.annotation_button.text() == "Annotation":
            self.annotation_button.setText("Visualization")
            self.set_bbox_items_editable = True
        else:
            self.annotation_button.setText("Annotation")
            self.set_bbox_items_editable = False
        self.bboxes_info_area.update_bboxes_info()    
    

if __name__ == '__main__':
    app = QApplication([])    
    root_dir = r"C:\Users\qj00241.7HORSE\Downloads\test_data\TlightClipData"
    clips_imgs_dir = os.path.join(root_dir, "tl_imgs")
    
    clip_name = "clp_1675339721350"
    clip_img_dir = os.path.join(clips_imgs_dir, clip_name)
    
    
    viewer = ImageViewer(clip_img_dir) # labels_dir
    viewer.show()
    app.exec_()
