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

lacked_clips = ['clp_1659351085600', 'clp_1666599265600', 'clp_1665224977900', 'clp_1667525855700', 'clp_1667464671000', 'clp_1667463991000', 'clp_1660819941600', 'clp_1666000981700', 'clp_1660128609899', 'clp_1667212611900', 'clp_1666078858099', 'clp_1660128689900', 'clp_1663758138000', 'clp_1667464651000', 'clp_1667527355700', 'clp_1667521735701', 'clp_1667533295700', 'clp_1666687025100', 'clp_1667527175701', 'clp_1666604428601', 'clp_1661942386400', 'clp_1665224497900', 'clp_1666001661700', 'clp_1667525915700', 'clp_1666594165600', 'clp_1667532315700', 'clp_1666592405300', 'clp_1666001981700', 'clp_1667541495700', 'clp_1665398696900', 'clp_1666691825100', 'clp_1666333278800', 'clp_1663757598000', 'clp_1666690305100', 'clp_1666690325100', 'clp_1666597505600', 'clp_1663758038000', 'clp_1667548235701', 'clp_1667377062600', 'clp_1665398536900', 'clp_1663757658000', 'clp_1665826910500', 'clp_1660819901600', 'clp_1666078798099', 'clp_1663757298000', 'clp_1666693565100', 'clp_1661942006400', 'clp_1666000621700', 'clp_1666321255601', 'clp_1666599205600', 'clp_1667212751900', 'clp_1663757958000', 'clp_1667532615700', 'clp_1667464731000', 'clp_1667532295700', 'clp_1666693725100', 'clp_1665221877899', 'clp_1667530895700', 'clp_1666599185600', 'clp_1663757978000', 'clp_1667528395701', 'clp_1666078838100', 'clp_1663758318000', 'clp_1667376822600', 'clp_1659350843200', 'clp_1667541435700', 'clp_1667526935701', 'clp_1666593965601', 'clp_1659351838000', 'clp_1667377042600', 'clp_1667530295700', 'clp_1665570072800', 'clp_1660128629900', 'clp_1661942666400', 'clp_1660819821601', 'clp_1659351872900', 'clp_1666684325100', 'clp_1667529995701', 'clp_1666950418700', 'clp_1663757738000', 'clp_1667464711000', 'clp_1666691425100', 'clp_1660819921600', 'clp_1665656131200', 'clp_1667530395701', 'clp_1666078778100', 'clp_1667541375700', 'clp_1661941786401', 'clp_1666690245100', 'clp_1666597485600', 'clp_1663229916700', 'clp_1661943386400', 'clp_1667529055700', 'clp_1663758558000', 'clp_1666686985100', 'clp_1666078918101', 'clp_1663757318000', 'clp_1660128489900', 'clp_1663758398000', 'clp_1663758078000', 'clp_1666686385100', 'clp_1661942446400', 'clp_1667541395700', 'clp_1660128549901', 'clp_1665224837901', 'clp_1663229796700', 'clp_1666088918100', 'clp_1665740870600', 'clp_1667464011000', 'clp_1666000021700', 'clp_1660819861600', 'clp_1660128389900', 'clp_1667548435700', 'clp_1663758518000', 'clp_1660128469901', 'clp_1667530415700', 'clp_1663758018000', 'clp_1665994561700', 'clp_1660819781600', 'clp_1667463711000', 'clp_1666684785100', 'clp_1665826890500', 'clp_1667529615700', 'clp_1666078818099', 'clp_1666950438700', 'clp_1661942966400', 'clp_1660819801600', 'clp_1666782810800', 'clp_1661941966401', 'clp_1661943066401', 'clp_1666693025100', 'clp_1667462471000', 'clp_1663758098000', 'clp_1667530335701', 'clp_1667463871000', 'clp_1663758178000', 'clp_1666082618100', 'clp_1666692145100', 'clp_1666598825600', 'clp_1665398936900', 'clp_1665826770500', 'clp_1665650251199', 'clp_1659352288899', 'clp_1661941826401', 'clp_1667531915700', 'clp_1661942226400', 'clp_1665650391201', 'clp_1665224817900', 'clp_1666687045100', 'clp_1667526775750', 'clp_1666949658700', 'clp_1659352081000', 'clp_1667289389501', 'clp_1663757418000', 'clp_1665398716900', 'clp_1666599025600', 'clp_1665649391199', 'clp_1667527215699', 'clp_1666777670800', 'clp_1663757698000', 'clp_1667531295700', 'clp_1666950458700', 'clp_1661943426400', 'clp_1660819981600', 'clp_1663758198000', 'clp_1666000681700', 'clp_1666779710800', 'clp_1667528415700', 'clp_1665398996900', 'clp_1667461811001', 'clp_1666597845600', 'clp_1666693005100', 'clp_1666078978101', 'clp_1664516280601', 'clp_1666687205100', 'clp_1663757178001', 'clp_1665395616900', 'clp_1666776770801', 'clp_1660819721600', 'clp_1667533275700', 'clp_1667548315700', 'clp_1663757638000', 'clp_1666599065600', 'clp_1663229776700', 'clp_1665309417500', 'clp_1663758478000', 'clp_1665395636900', 'clp_1666690285100', 'clp_1667462211000', 'clp_1666686465100', 'clp_1666597765600', 'clp_1667376322600', 'clp_1663757198000', 'clp_1659351803300', 'clp_1667548375700', 'clp_1667546275700', 'clp_1665994541700', 'clp_1663757878000', 'clp_1666686365100', 'clp_1667464871000', 'clp_1666321295600', 'clp_1667377222601', 'clp_1666684985100', 'clp_1665309457500', 'clp_1665395896900', 'clp_1665650171201', 'clp_1667522135701', 'clp_1663757778001', 'clp_1667547055700', 'clp_1666592445300', 'clp_1660128349899', 'clp_1666599145600', 'clp_1667531575700', 'clp_1661942946401', 'clp_1659351120200', 'clp_1660128449901', 'clp_1659087204499', 'clp_1666777410800', 'clp_1663757718000', 'clp_1667527195701', 'clp_1663757498000', 'clp_1667529815700', 'clp_1661943126400', 'clp_1667464091000', 'clp_1666002061700', 'clp_1660128409900', 'clp_1666597605600', 'clp_1666777570800', 'clp_1667212771900', 'clp_1667529855700', 'clp_1667533375700', 'clp_1667530055700', 'clp_1667526415700', 'clp_1665650231200', 'clp_1667377202600', 'clp_1666082698099', 'clp_1667531995750', 'clp_1666687305101', 'clp_1665309557501', 'clp_1666082538101', 'clp_1667526575700', 'clp_1661942146400', 'clp_1667522075701', 'clp_1666597405601', 'clp_1667289469500', 'clp_1667529795700', 'clp_1667289449500', 'clp_1661942186400', 'clp_1666087678099', 'clp_1661942106400', 'clp_1667461791000', 'clp_1663757238000', 'clp_1665649351200', 'clp_1660819761600', 'clp_1663757538001', 'clp_1663758498001', 'clp_1661942086400', 'clp_1659351733800', 'clp_1666687005100', 'clp_1667546955700', 'clp_1666686425100', 'clp_1666779530800', 'clp_1667464031000', 'clp_1666685005100', 'clp_1665649371200', 'clp_1666597685600', 'clp_1666002001700', 'clp_1666606408600', 'clp_1666592425300', 'clp_1667548595700', 'clp_1663758058000', 'clp_1663758458000']
interested_clips = ['clp_1668415709400', 'clp_1668417549400', 'clp_1660131727100', 'clp_1668496857101', 'clp_1668391629300', 'clp_1668505537099', 'clp_1668652342900', 'clp_1668416289400', 'clp_1668647522900', 'clp_1672912248551', 'clp_1668483342400', 'clp_1668566578100', 'clp_1660131087100', 'clp_1668480902399', 'clp_1668651162900', 'clp_1675239878949', 'clp_1668657226200', 'clp_1668418289401', 'clp_1668414669400', 'clp_1668653022900', 'clp_1668658866201', 'clp_1668564338100', 'clp_1668654442900', 'clp_1668504917101', 'clp_1668670449200', 'clp_1668406804701', 'clp_1668148643600', 'clp_1665398956900', 'clp_1668146163600', 'clp_1665224157900', 'clp_1668395549300', 'clp_1668562718100', 'clp_1668673589201', 'clp_1668506697100', 'clp_1668506197099', 'clp_1668392549300', 'clp_1668416249400', 'clp_1660130987100', 'clp_1668665129199', 'clp_1668569478150', 'clp_1660131347100', 'clp_1668413069399', 'clp_1668580280600', 'clp_1668649262900', 'clp_1660131207100', 'clp_1668405244700', 'clp_1659091733900', 'clp_1668149623651', 'clp_1668418309401', 'clp_1668406724701', 'clp_1668656406201', 'clp_1668566658100', 'clp_1668566818100', 'clp_1668649122900', 'clp_1668393149300', 'clp_1660131927100', 'clp_1668413489400', 'clp_1668496457100', 'clp_1660130947100', 'clp_1668417249400', 'clp_1668408164700', 'clp_1668407284700', 'clp_1668500737101', 'clp_1668658546200', 'clp_1668484582400', 'clp_1668495857150', 'clp_1668148243600', 'clp_1672910468551', 'clp_1668506857101', 'clp_1672824047650', 'clp_1668664649200', 'clp_1668657206201', 'clp_1660131307100', 'clp_1668504837099', 'clp_1672910588550', 'clp_1668418609400', 'clp_1668397589300', 'clp_1660131527100', 'clp_1666692665100', 'clp_1668583560601', 'clp_1659087622399', 'clp_1660131247100', 'clp_1668415089400', 'clp_1668506877099', 'clp_1675757696150', 'clp_1668653222900', 'clp_1668647402900', 'clp_1666312440400', 'clp_1668391909300', 'clp_1668416009400', 'clp_1668408364700', 'clp_1668147223600', 'clp_1668562998100', 'clp_1660131747100', 'clp_1668390409300', 'clp_1675665457950', 'clp_1668563878100', 'clp_1667214531950', 'clp_1675767196151', 'clp_1664443532900', 'clp_1659350808600', 'clp_1668413449400', 'clp_1672737586250', 'clp_1668481482399', 'clp_1660131947100', 'clp_1660131367100', 'clp_1668483942400', 'clp_1668571158100', 'clp_1668412369399', 'clp_1668408524700', 'clp_1668412509400', 'clp_1668391929300', 'clp_1660131407100', 'clp_1668405404700', 'clp_1668406384700', 'clp_1667785525001', 'clp_1666684185100', 'clp_1668506897101', 'clp_1660131467100', 'clp_1668652702900', 'clp_1668505477099', 'clp_1659352219600', 'clp_1660131587100', 'clp_1668658566200', 'clp_1668149743599', 'clp_1660132007100', 'clp_1671176953900', 'clp_1660131387100', 'clp_1668418809399', 'clp_1668395889300', 'clp_1668146783650', 'clp_1668397389300', 'clp_1668505217099', 'clp_1675339721350', 'clp_1668481182400', 'clp_1667462711001', 'clp_1659350739200', 'clp_1668566458100', 'clp_1668561198100', 'clp_1660131067100', 'clp_1668417529400', 'clp_1668405824700', 'clp_1668389989300', 'clp_1668664749200', 'clp_1668664849200', 'clp_1668670089200', 'clp_1668396149300', 'clp_1668498077100', 'clp_1668498277100', 'clp_1660131687100', 'clp_1667527955701', 'clp_1667525795700', 'clp_1671082205300', 'clp_1668415849401', 'clp_1668395169300', 'clp_1660131047100', 'clp_1668405884700', 'clp_1675307812850', 'clp_1668412569401', 'clp_1668672669201', 'clp_1668412749401', 'clp_1672910428550', 'clp_1660131707100', 'clp_1671175993901', 'clp_1668389529300', 'clp_1668395069300', 'clp_1668483622400', 'clp_1668505517099', 'clp_1668389049300', 'clp_1660131567100', 'clp_1668405544700', 'clp_1668669429201', 'clp_1660131187100', 'clp_1668416309400', 'clp_1659086193300', 'clp_1672911868550', 'clp_1668408324700', 'clp_1660131547100', 'clp_1668392569300', 'clp_1668657466200', 'clp_1659350947000', 'clp_1668648302900']
preblink_clips = ['clp_1668418349400', 'clp_1660131967100', 'clp_1660131267100', 'clp_1671175733899', 'clp_1668584080600', 'clp_1668648282902', 'clp_1668405864701', 'clp_1659351154800', 'clp_1668671989200', 'clp_1668560718100', 'clp_1668504877101', 'clp_1668408124701', 'clp_1668665029200', 'clp_1668149643600', 'clp_1668405764700', 'clp_1668564378100', 'clp_1668414949399', 'clp_1660130927100', 'clp_1668146523600', 'clp_1668405644700', 'clp_1665398896900', 'clp_1672132344251', 'clp_1668505117100', 'clp_1672910988550', 'clp_1668657506201', 'clp_1659087239200', 'clp_1668396769300', 'clp_1668648182900', 'clp_1668416729400', 'clp_1672826407650', 'clp_1668646882900', 'clp_1668506737101', 'clp_1668049328300', 'clp_1668415989402', 'clp_1668414809401', 'clp_1660131887101', 'clp_1668563918100', 'clp_1668561278100', 'clp_1668667629199', 'clp_1668415829401', 'clp_1668563058100', 'clp_1672824407650', 'clp_1668646922900', 'clp_1668578260600', 'clp_1668392149300', 'clp_1668580320601', 'clp_1668505637101', 'clp_1668669389201', 'clp_1668505297101', 'clp_1668483962399', 'clp_1668415789400', 'clp_1668506637101', 'clp_1660132087100', 'clp_1668652302900', 'clp_1668405804700', 'clp_1668506997100', 'clp_1668416949401', 'clp_1672911808551', 'clp_1675336436550', 'clp_1672132944250', 'clp_1668415809400', 'clp_1660131987101', 'clp_1668397369300', 'clp_1660131227100', 'clp_1668418529400', 'clp_1660131667100', 'clp_1668148843600', 'clp_1668506037099', 'clp_1668655986199', 'clp_1668413669399', 'clp_1668583700600', 'clp_1668656466200', 'clp_1675335859150', 'clp_1668562938100', 'clp_1668049448299', 'clp_1668669709201', 'clp_1672132324251', 'clp_1668654502900', 'clp_1659351601299', 'clp_1668146443601', 'clp_1668149803600', 'clp_1668413989401', 'clp_1668389369300', 'clp_1668484002400', 'clp_1668505137100', 'clp_1668406684699', 'clp_1672912628550', 'clp_1668562538100', 'clp_1668405784700', 'clp_1665398556900', 'clp_1668414629400', 'clp_1660131327100', 'clp_1668506617100', 'clp_1668563158100', 'clp_1668150923600', 'clp_1668405924700', 'clp_1668406124700', 'clp_1668482502400', 'clp_1668506597100', 'clp_1668563898100', 'clp_1668496097100', 'clp_1668504857150', 'clp_1675238321050', 'clp_1668567778150', 'clp_1668397229300', 'clp_1659351224100']
interested_clips = interested_clips + preblink_clips

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
            if self.image_viewer.highlighted_bbox_id:
                item = self.image_viewer.bboxes_info_area.currentItem()
                if item:
                    bbox_id = item.data(1, Qt.UserRole)
                    self.image_viewer.clip.delete_label_by_index(self.image_viewer.current_index, bbox_id, filtered=self.image_viewer.edit_filtered_track)
            else:
                self.image_viewer.clip.delete_label_by_index(self.image_viewer.current_index, bbox_id=None, filtered=self.image_viewer.edit_filtered_track)
            self.image_viewer.print_screen()
        elif event.key() == Qt.Key_D:
            print('D key pressed')
        else:
            super().keyPressEvent(event)

class ImageViewer(QWidget):
    def __init__(self, root_clip_dir):
        super().__init__()
        self.clip_dirs = [os.path.join(root_clip_dir, clip_name) for clip_name in os.listdir(root_clip_dir) 
                          if clip_name.startswith("clp") and os.path.isdir(os.path.join(root_clip_dir, clip_name))]
        
        self.clip_dir_labeled_flag_dict = {}
        for clip_dir in self.clip_dirs:
            self.clip_dir_labeled_flag_dict[clip_dir] = CLIP.get_labeled_flag(clip_dir)
        
        self.clip_dir = self.clip_dirs[0]
        self.clip = CLIP(self.clip_dir)

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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_K:
            if self.current_index==0:
                return
            self.set_current_index(self.current_index-1)
        elif event.key() == Qt.Key_L:
            self.set_current_index(self.current_index+1)

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

        # 创建一个包含clip路径的列表窗口
        self.clip_list = QListWidget()
        for clip_dir in self.clip_dirs:
            clip_name = clip_dir.split('\\')[-1]
            item = QListWidgetItem(clip_name)
            if self.clip_dir_labeled_flag_dict[clip_dir]:
                item.setForeground(QColor("red"))
            elif clip_name in interested_clips:
                item.setForeground(QColor("blue"))
            elif clip_name in lacked_clips:
                item.setForeground(QColor("gray"))
            self.clip_list.addItem(item)

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

        clip_basic_tab = QWidget()
        clip_basic_layout = QVBoxLayout()
        clip_basic_layout.addWidget(self.clip_list)
        clip_basic_tab.setLayout(clip_basic_layout)
        self.tab_widget.addTab(clip_basic_tab, "Clip Selection")

        # 创建 Basic 选项卡
        basic_tab = QWidget()
        basic_layout = QVBoxLayout()

        # 添加 Annotation 按钮
        self.annotation_button = QPushButton("Annotation", self)
        self.annotation_button.clicked.connect(self.toggle_annotation_button)
        basic_layout.addWidget(self.annotation_button)
        self.annotation_button.setText("Visualization")

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
        
        run_hot_sequence_labeler_button = QPushButton("Run Hot Sequence Labeler and Blinker")
        run_hot_sequence_labeler_button.clicked.connect(self.run_hot_sequence_labeler_and_print_screen)
        operation_layout.addWidget(run_hot_sequence_labeler_button, len(self.input_widgets)+len(self.input_widgets_labeler)+2, 0, 1, 2)
       
        run_export_label_button = QPushButton("Export Label")
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
        self.clip_list.currentRowChanged.connect(self.set_current_clip)
        self.image_list.currentRowChanged.connect(self.set_current_index)
        
        # 设置初始状态
        self.current_index = 0
        self.highlighted_track_id = None
        self.highlighted_bbox_id = None
        self.set_bbox_items_editable = True
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

    def set_current_clip(self, index):
        self.clip_dir = self.clip_dirs[index]
        self.clip = CLIP(self.clip_dir)
        self.image_paths = self.clip.get_all_image_paths()
        
        self.image_list = QListWidget()
        for img_path in self.image_paths:
            item = QListWidgetItem(img_path)
            self.image_list.addItem(item)
        self.image_list.currentRowChanged.connect(self.set_current_index)
        self.slider.setMaximum(len(self.image_paths) - 1)

        basic_tab = QWidget()
        basic_layout = QVBoxLayout()

        # 添加 Annotation 按钮
        self.annotation_button = QPushButton("Annotation", self)
        self.annotation_button.clicked.connect(self.toggle_annotation_button)
        basic_layout.addWidget(self.annotation_button)
        self.annotation_button.setText("Visualization")

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
        basic_layout.addWidget(self.image_list)
        basic_tab.setLayout(basic_layout)

        self.tab_widget.removeTab(1)
        self.tab_widget.insertTab(1, basic_tab, "Basic")
        
        if self.clip_dir_labeled_flag_dict[self.clip_dir]:
            self.show_bbox.setChecked(False)
            self.show_track.setChecked(False)
            self.show_filtered_bbox.setChecked(True)
            self.show_filtered_track.setChecked(True)
        else:
            self.show_bbox.setChecked(True)
            self.show_track.setChecked(True)
            self.show_filtered_bbox.setChecked(False)
            self.show_filtered_track.setChecked(False)
        
        self.set_current_index(0)
        

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
        self.clip.run_blinker()
        self.info_text_edit.append("Run Hot Squence Labeler and Blinker: Success!\n")
        self.show_bbox.setChecked(False)
        self.show_track.setChecked(False)
        self.show_filtered_bbox.setChecked(True)
        self.show_filtered_track.setChecked(True)
        self.print_screen()

    def run_export_label(self):
        self.clip.export_filtered_annos()
        self.clip_dir_labeled_flag_dict[self.clip_dir] = CLIP.get_labeled_flag(self.clip_dir)
        
        # 重新显示Clip Selection
        self.clip_list = QListWidget()
        for clip_dir in self.clip_dirs:
            clip_name = clip_dir.split('\\')[-1]
            item = QListWidgetItem(clip_name)
            if self.clip_dir_labeled_flag_dict[clip_dir]:
                item.setForeground(QColor("red"))
            elif clip_name in interested_clips:
                item.setForeground(QColor("blue"))
            elif clip_name in lacked_clips:
                item.setForeground(QColor("gray"))
            self.clip_list.addItem(item)
        self.clip_list.currentRowChanged.connect(self.set_current_clip)
            
        clip_basic_tab = QWidget()
        clip_basic_layout = QVBoxLayout()
        clip_basic_layout.addWidget(self.clip_list)
        clip_basic_tab.setLayout(clip_basic_layout)
        self.tab_widget.removeTab(0)
        self.tab_widget.insertTab(0, clip_basic_tab, "Clip Selection")
            
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
    # root_dir = r"C:\Users\qj00241.7HORSE\Downloads\test_data\TlightClipData"
    # clips_imgs_dir = os.path.join(root_dir, "tl_imgs")
    clips_imgs_dir = r"D:\label\6.2-2" # 6.2-2
    # clip_name = "clp_1675339721350"
    # clip_img_dir = os.path.join(clips_imgs_dir, clip_name)
    
    
    viewer = ImageViewer(clips_imgs_dir) # labels_dir
    viewer.show()
    app.exec_()
