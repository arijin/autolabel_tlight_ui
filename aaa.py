import os
import json

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QBrush
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QSlider, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox

from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QSplitter, QInputDialog, QScrollArea, QTreeWidget, QTreeWidgetItem
# from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QDialog, QRadioButton, QButtonGroup, QTextEdit

from PyQt5.QtWidgets import QLabel, QRadioButton, QVBoxLayout, QPushButton, QDialog, QButtonGroup, QGridLayout

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from module import CLIP, BBOX





class ImageViewer(QWidget):
    def __init__(self, clip_dir):
        super().__init__()
        self.clip_dir = clip_dir
        self.clip = CLIP(clip_dir)

        # 获取图片文件列表
        self.image_paths = self.clip.get_all_image_paths()
        self.show_bbox_color = True
        self.show_bbox_blink_state = False

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
        self.slider.setMaximum(len(self.image_paths) - 1)

        # 创建控制按钮
        self.play_button = QPushButton('Play', self)

        # 创建水平布局，并添加滑块和控制按钮
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.slider)
        control_layout.addWidget(self.play_button)

        self.show_bbox = QCheckBox('Show BBox', self)
        control_layout.addWidget(self.show_bbox)
        self.show_bbox.stateChanged.connect(self.print_screen)
        
        self.show_track = QCheckBox('Show Track', self)
        control_layout.addWidget(self.show_track)
        self.show_track.stateChanged.connect(self.print_screen)

        # 创建垂直布局，并添加图片标签和控制布局
        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        # layout.addWidget(self.image_label)
        layout.addWidget(self.coord_label)
        layout.addLayout(control_layout)

        # 创建一个包含图片路径的列表窗口
        self.image_list = QListWidget()

        # 添加图片到 image_list
        for img_path in self.image_paths:
            item = QListWidgetItem(img_path)
            self.image_list.addItem(item)

        # 在图片列表下方添加跟踪信息显示区域
        self.tracking_info_area = QTreeWidget()
        self.tracking_info_area.setHeaderHidden(True)

        # 将图片列表和跟踪信息显示区域放入一个垂直布局
        left_side_layout = QVBoxLayout()
        left_side_layout.addWidget(self.image_list)
        left_side_layout.addWidget(self.tracking_info_area)

        # 使用QSplitter将图片列表和跟踪信息显示区域的布局与现有布局分开
        splitter = QSplitter(Qt.Horizontal)
        left_side_widget = QWidget()
        left_side_widget.setLayout(left_side_layout)
        splitter.addWidget(left_side_widget)

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
        self.tracking_info_area.itemClicked.connect(self.on_tracking_info_item_clicked)

        # 设置初始状态
        self.current_index = 0
        self.highlighted_track_id = None
        self.playing = False
        self.update_tracking_info()  # 在初始化UI时调用更新跟踪信息的方法
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


    def update_bbox_class_id(self, label_path, bbox_index, new_class_id):


    def set_current_index(self, value):

    def toggle_play(self):


    def update_image(self):


    def print_image(self):

    
    def print_screen(self):


    def update_tracking_info(self):


    def on_tracking_info_item_clicked(self, item, column):




if __name__ == '__main__':
    app = QApplication([])    
    root_dir = r"C:\Users\qj00241.7HORSE\Downloads\test_data\TlightClipData"
    clips_imgs_dir = os.path.join(root_dir, "tl_imgs")
    
    clip_name = "clp_1675339721350"
    clip_img_dir = os.path.join(clips_imgs_dir, clip_name)
    
    
    viewer = ImageViewer(clip_img_dir) # labels_dir
    viewer.show()
    app.exec_()
