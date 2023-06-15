import os

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QBrush
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QSlider, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox

from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QSplitter

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
    no_blink, blink = 220, 255
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

        # 创建显示图片的标签
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 400)

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
        layout.addWidget(self.image_label)
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
