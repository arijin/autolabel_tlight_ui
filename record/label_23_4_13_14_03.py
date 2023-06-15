import os

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QBrush
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QSlider, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox

from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QSplitter, QInputDialog, QScrollArea
# from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QDialog, QRadioButton, QButtonGroup

class RadioButtonDialog(QDialog):
    def __init__(self, class_ids, current_class_id, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Select Class ID")
        layout = QVBoxLayout()

        self.button_group = QButtonGroup(self)

        for class_id, class_name in class_ids.items():
            radio_button = QRadioButton(f"{class_id}: {class_name}")
            self.button_group.addButton(radio_button, class_id)
            layout.addWidget(radio_button)

            if class_id == current_class_id:
                radio_button.setChecked(True)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

        self.setLayout(layout)

    def selected_class_id(self):
        return self.button_group.checkedId()

def get_class_name(class_id):
    class_dict = {
        0: "green",
        1: "red",
        2: "yellow",
        3: "black",
        4: "green_blink",
        5: "red_blink",
        6: "yellow_blink",
        7: "unknown",
    }
    if class_id<len(class_dict):
        return class_dict[class_id]
    else:
        raise ValueError("over-class id: {}".format(class_id))

def get_class_id(class_name):
    class_dict = {
        "green": 0,
        "red": 1,
        "yellow": 2,
        "black": 3,
        "green_blink": 4,
        "red_blink": 5,
        "yellow_blink": 6,
        "unknown": 7,
        "black_blink": 4 # Temporal
    }
    if class_name in class_dict:
        return class_dict[class_name]
    else:
        raise ValueError("Unknown class name: {}".format(class_name))
    
def get_class_color(class_id):
    no_blink, blink = 255, 255
    class_dict = {
        0: (0, 255, 0    , no_blink),
        1: (255, 0, 0    , no_blink),
        2: (255, 255, 0  , no_blink),
        3: (255, 255, 255, no_blink),
        4: (0, 255, 0    , blink),
        5: (255, 0, 0    , blink),
        6: (255, 255, 0  , blink),
        7: (128, 128, 128, blink)
    }
    if class_id<len(class_dict):
        return class_dict[class_id]
    else:
        raise ValueError("over-class id: {}".format(class_id))

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

class ImageViewer(QWidget):
    def __init__(self, images_dir, labels_dir):
        super().__init__()
        self.images_dir = images_dir
        self.labels_dir = labels_dir

        # 获取图片文件列表
        self.images = sorted(os.listdir(images_dir))
        self.labels = sorted(os.listdir(labels_dir))

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
        self.image_label.setMouseTracking(True)

        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)  # 设置为可调整大小

        # 创建滑块
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.images) - 1)

        # 创建控制按钮
        self.play_button = QPushButton('Play', self)

        # 创建水平布局，并添加滑块和控制按钮
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.slider)
        control_layout.addWidget(self.play_button)

        self.show_bbox = QCheckBox('Show BBox', self)
        control_layout.addWidget(self.show_bbox)
        self.show_bbox.stateChanged.connect(self.print_screen)

        # 创建垂直布局，并添加图片标签和控制布局
        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        # layout.addWidget(self.image_label)
        layout.addWidget(self.coord_label)
        layout.addLayout(control_layout)

        # 创建一个包含图片路径的列表窗口
        self.image_list = QListWidget()

        # 添加图片到 image_list
        for img_path in self.images:
            item = QListWidgetItem(img_path)
            self.image_list.addItem(item)

        # 使用QSplitter将图片列表和现有布局分开
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.image_list)

        main_widget = QWidget()
        main_widget.setLayout(layout)
        splitter.addWidget(main_widget)

        # 设置初始窗口部件宽度
        splitter.setSizes([100, 700])

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(splitter)

        # 为控件添加事件处理函数
        self.slider.valueChanged.connect(self.set_current_index)
        self.play_button.clicked.connect(self.toggle_play)
        self.image_list.currentRowChanged.connect(self.set_current_index)

        # 设置初始状态
        self.current_index = 0
        self.playing = False
        self.print_screen()


    def image_label_clicked(self, event):
        x, y = event.pos().x(), event.pos().y()
        self.select_bbox(x, y)

    def get_scale_ratio(self):
        pixmap_size = self.image_label.pixmap().size()
        label_size = self.image_label.size()
        x_ratio, y_ratio = label_size.width() / pixmap_size.width(), label_size.height() / pixmap_size.height()
        return (x_ratio, y_ratio)

    def select_bbox(self, x, y):
        x_ratio, y_ratio = self.get_scale_ratio()
        original_x = int(x / x_ratio)
        original_y = int(y / y_ratio)

        label_path = os.path.join(self.labels_dir, self.labels[self.current_index])
        with open(label_path, 'r') as f:
            lines = f.readlines()

        selected_bbox = None
        for index, line in enumerate(lines):
            label = line.strip().split(' ')
            x1, y1, x2, y2 = map(int, label[1:-1])
            selected_class_id  = get_class_id(label[-1])
            if x1 <= original_x <= x2 and y1 <= original_y <= y2:
                selected_bbox = index
                break

        if selected_bbox is not None:
            class_ids = {
                0: "green",
                1: "red",
                2: "yellow",
                3: "black",
                4: "green_blink",
                5: "red_blink",
                6: "yellow_blink",
                7: "unknown"
            }
            # 创建一个列表存储类ID和对应的颜色名称
            options = [f"{class_id}: {class_name}" for class_id, class_name in class_ids.items()]
            # 显示包含所有选项的对话框
            # selected_item, ok = QInputDialog.getItem(self, "Select Class ID", "Class:", options, selected_class_id, False)
            # new_class_id = int(selected_item.split(':')[0])
            # if ok:
            #     self.update_bbox_class_id(label_path, selected_bbox, new_class_id)
            #     self.print_screen()
            dialog = RadioButtonDialog(class_ids, selected_class_id, self)
            result = dialog.exec_()
            if result == QDialog.Accepted:
                new_class_id = dialog.selected_class_id()
                self.update_bbox_class_id(label_path, selected_bbox, new_class_id)
                self.print_screen()

    def update_bbox_class_id(self, label_path, bbox_index, new_class_id):
        with open(label_path, 'r') as f:
            lines = f.readlines()

        new_class_name = get_class_name(new_class_id) # 根据class_id找到对应的class_name
        bbox_info = lines[bbox_index].strip().split(' ')
        bbox_info[-1] = new_class_name
        new_line = ' '.join(bbox_info) + '\n'
        lines[bbox_index] = new_line

        with open(label_path, 'w') as f:
            f.writelines(lines)

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
            if self.current_index >= len(self.images):
                self.current_index = 0
                self.playing = False
            self.print_screen()
            self.slider.setValue(self.current_index)
        else:
            self.play_button.setText('Play')

    def print_image(self):
        image_path = os.path.join(self.images_dir, self.images[self.current_index])
        image = QPixmap(image_path)
        self.image_label.setPixmap(image)
        # scaled_image = image.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # self.image_label.setPixmap(scaled_image)
    
    def print_screen(self):
        self.print_image()
        
        # 绘制 bounding box
        if self.show_bbox.isChecked():
            painter = QPainter(self.image_label.pixmap())
            # 读取对应帧的标签文件
            label_path = os.path.join(self.labels_dir, self.labels[self.current_index])
            with open(label_path, 'r') as f:
                lines = f.readlines()
            for line in lines:
                label = line.strip().split(' ')
                # 绘制 bounding box
                x1, y1, x2, y2 = map(int, label[1:-1])
                class_name = label[-1]
                class_id = get_class_id(class_name)
                
                pen_size = max(1, min(x2 - x1, y2 - y1) // 5)  # 设置画笔的粗细，最小为1，最大为bounding box宽高中的较小值的1/50
                color = get_class_color(class_id)
                pen = QPen(QColor(*color), pen_size)  # 设置画笔颜色和粗细
                painter.setPen(pen)
                painter.drawRect(x1, y1, x2 - x1, y2 - y1)
                
                if "blink" in class_name:
                    # 绘制blink圆形
                    radius = (x2 - x1) // 2.5
                    painter.setPen(QPen(Qt.NoPen))
                    painter.setBrush(QBrush(QColor(255, 165, 0, 255)))
                    if y1 - radius*2 > radius:
                        painter.drawEllipse((x1 + x2) // 2 - radius, y1 - radius*3, radius * 2, radius * 2)
                    else:
                        painter.drawEllipse((x1 + x2) // 2 - radius, y2 + radius*3, radius * 2, radius * 2)
            painter.end()


if __name__ == '__main__':
    app = QApplication([])
    images_dir = r"C:\Users\qj00241\Downloads\MLT\tl_imgs\dishui_lake_1"
    labels_dir = r"C:\Users\qj00241\Downloads\MLT\tl_labels\dishui_lake_1"
    viewer = ImageViewer(images_dir, labels_dir)
    viewer.show()
    app.exec_()
