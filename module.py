import os
import json
from collections import defaultdict

import numpy as np
from tqdm import tqdm

from models.ByteTrack.tracker2.byte_tracker import BYTETracker, TrackState

class CLIP_Base(object):
    def __init__(self, clip_img_dir):
        self.clip_img_dir = clip_img_dir
        self.frames, self.annos = self.read_clip(clip_img_dir)
        assert len(self.frames) == len(self.annos)
        self.filtered_annos = self.read_filtered_annos(clip_img_dir)
        if not self.filtered_annos:
            self.filtered_annos = [{'image_name': anno['image_name'], 'bboxes_anno': []} for anno in self.annos]
    
    @staticmethod
    def get_labeled_flag(clip_img_dir):
        clip_json_path = os.path.join(clip_img_dir, "metadata.json")
        with open(clip_json_path, 'r') as f:
            clip_data = json.load(f)
        if 'filtered_anno' in clip_data.keys():
            return True
        else:
            return False
    
    @property
    def image_paths(self):
        return self.get_all_image_paths()
    
    @property
    def bboxes_frames(self):
        return self.get_all_labels(self.annos)
    
    @property
    def filtered_bboxes_frames(self):
        return self.get_all_labels(self.filtered_annos)
    
    @property
    def tracking_info(self):
        return self.get_tracking_info(self.annos)
    
    @property
    def filtered_tracking_info(self):
        return self.get_tracking_info(self.filtered_annos)
    
    def read_clip(self, clip_img_dir):
        clip_json_path = os.path.join(clip_img_dir, "metadata.json")
        with open(clip_json_path, 'r') as f:
            clip_data = json.load(f)
        object_detection_state = clip_data['brush_info']['object_detection']
        color_detection = clip_data['brush_info']['color_detection']
        blink_state_detection = clip_data['brush_info']['blink_state_detection']
        object_tracking = clip_data['brush_info']['object_tracking']
        
        frames = clip_data['frames']
        annos = clip_data['anno']
        
        return frames, annos

    def read_filtered_annos(self, clip_img_dir):
        clip_json_path = os.path.join(clip_img_dir, "metadata.json")
        with open(clip_json_path, 'r') as f:
            clip_data = json.load(f)
        if 'filtered_anno' in clip_data.keys():
            filtered_anno = clip_data['filtered_anno']
        else:
            filtered_anno = None
        return filtered_anno

    def get_all_image_paths(self):
        image_paths = []
        for frame in self.frames:
            image_path = os.path.join(self.clip_img_dir, frame['image_name'])
            image_paths.append(image_path)
        return image_paths
    
    def get_all_labels(self, annos):
        bboxes_frames = []
        for anno in annos:
            bboxes = {}
            for bbox_anno in anno['bboxes_anno']:
                bbox = BBOX(bbox_anno)
                bboxes.update({bbox.bbox_id: bbox})
                # bboxes.append(bbox)
            bboxes_frames.append(bboxes)
        return bboxes_frames

    def get_tracking_info(self, annos):
        # 初始化字典存储跟踪信息
        tracking_list = defaultdict(lambda: {'start_frame': None, 'end_frame': None, 'start_frame_name': None, 'end_frame_name': None, 'frame_count': 0, 'total_confidence': 0.0, 'lost_frames': []})
        
        bboxes_frames = self.get_all_labels(annos)
        # 遍历每个文件并解析跟踪结果
        for frame_idx, frame_bboxes in enumerate(bboxes_frames):
            for bbox in frame_bboxes.values():
                if bbox.track_id==-1:
                    continue
                track_id = bbox.track_id
                confidence = bbox.det_confidence
                
                # 更新跟踪信息
                if tracking_list[track_id]['start_frame'] is None:
                    tracking_list[track_id]['start_frame'] = frame_idx + 1
                tracking_list[track_id]['end_frame'] = frame_idx + 1
                tracking_list[track_id]['frame_count'] += 1
                tracking_list[track_id]['total_confidence'] += confidence
        
        tracking_info = []
        for id, info in tracking_list.items():
            avg_confidence = info['total_confidence'] / info['frame_count']
            tracking_info.append({'id': id, 'start_frame': info['start_frame'], 'end_frame': info['end_frame'],
                                  'frame_count': info['frame_count'], 'average_confidence': round(avg_confidence, 2)})
        
        return tracking_info
    
    def get_len_frames(self):
        return len(self.frames)
    
    def get_image_path_by_index(self, frame_index):
        return self.image_paths[frame_index]
    
    def get_label_by_index(self, frame_index, filtered=False):
        if filtered:
            return self.filtered_bboxes_frames[frame_index]
        else:
            return self.bboxes_frames[frame_index]
    
    def get_filtered_label_by_index(self, frame_index):
        return self.filtered_bboxes_frames[frame_index]
    
    def set_label_by_index(self, frame_index, bbox_id, bbox):
        for bbox_anno in self.annos[frame_index]['bboxes_anno']:
            if bbox_anno['bbox_id'] == bbox_id:
                BBOX.set_bbox_anno(bbox_anno, bbox)

    def delete_label_by_index(self, frame_index, bbox_id, filtered=False):
        if filtered:
            annos = self.filtered_annos
        else:
            annos = self.annos
            
        if bbox_id:
            for bbox_anno in annos[frame_index]['bboxes_anno']:
                if bbox_anno['bbox_id'] == bbox_id:
                    annos[frame_index]['bboxes_anno'].remove(bbox_anno)
                    break
        else:
            for frame_index, frame_annos in enumerate(self.annos[:frame_index+1]):
                for bbox_anno in frame_annos['bboxes_anno'][:]:
                    annos[frame_index]['bboxes_anno'].remove(bbox_anno)
    
    def delete_label_by_track_id(self, track_id):
        for frame_index, frame_annos in enumerate(self.annos[:]):
            for bbox_anno in frame_annos['bboxes_anno']:
                if bbox_anno['attr']['track_id']== track_id:
                    self.annos[frame_index]['bboxes_anno'].remove(bbox_anno)
                    break
        return
    
    def delete_filtered_label_by_track_id(self, track_id):
        for frame_index, frame_annos in enumerate(self.filtered_annos[:]):
            for bbox_anno in frame_annos['bboxes_anno']:
                if bbox_anno['attr']['track_id']== track_id:
                    self.filtered_annos[frame_index]['bboxes_anno'].remove(bbox_anno)
                    break
        return
    
    def add_filtered_label_by_track_id(self, track_id):
        for frame_index, frame_annos in enumerate(self.annos[:]):
            for bbox_anno in frame_annos['bboxes_anno']:
                if bbox_anno['attr']['track_id']== track_id:
                    self.filtered_annos[frame_index]['bboxes_anno'].append(bbox_anno)
                    self.annos[frame_index]['bboxes_anno'].remove(bbox_anno)
        return
    
    def undo_filtered_label_by_track_id(self, track_id):
        for frame_index, frame_annos in enumerate(self.filtered_annos[:]):
            for bbox_anno in frame_annos['bboxes_anno']:
                if bbox_anno['attr']['track_id']== track_id:
                    self.annos[frame_index]['bboxes_anno'].append(bbox_anno)
                    self.filtered_annos[frame_index]['bboxes_anno'].remove(bbox_anno)
        return
    
    def set_label_color_blink_state_by_index(self, frame_index, bbox_id, new_color, new_blink_state, filtered=False):
        if filtered:
            annos = self.filtered_annos
        else:
            annos = self.annos
            
        for bbox_anno in annos[frame_index]['bboxes_anno']:
            if bbox_anno['bbox_id']==bbox_id:
                bbox_anno['attr']['color'] = new_color
                bbox_anno['attr']['blink_state'] = new_blink_state
    
    def set_label_track_id_last_frames(self, frame_index, previous_track_id, target_track_id):
        for frame_annos in self.annos[frame_index:]:
            for bbox_anno in frame_annos['bboxes_anno']:
                if bbox_anno['attr']['track_id']==previous_track_id:
                    bbox_anno['attr']['track_id'] = target_track_id
                    break
    
    def switch_label_track_id_last_frames(self, frame_index, previous_track_id, target_track_id, filtered=False):
        if filtered:
            annos = self.filtered_annos
        else:
            annos = self.annos
            
        for frame_annos in annos[frame_index:]:
            has_previous_track_id = False
            has_target_track_id = False
            for bbox_anno in frame_annos['bboxes_anno']:
                if bbox_anno['attr']['track_id']==previous_track_id:
                    has_previous_track_id = True
                elif bbox_anno['attr']['track_id']==target_track_id:
                    has_target_track_id = True
            for bbox_anno in frame_annos['bboxes_anno']:
                if has_previous_track_id and has_target_track_id:
                    if bbox_anno['attr']['track_id']==target_track_id:
                        bbox_anno['attr']['track_id'] = previous_track_id
                    elif bbox_anno['attr']['track_id']==previous_track_id:
                        bbox_anno['attr']['track_id'] = target_track_id
                else:
                    if bbox_anno['attr']['track_id']==previous_track_id:
                        bbox_anno['attr']['track_id'] = target_track_id
                   
    def export_filtered_annos(self):
        clip_json_path = os.path.join(self.clip_img_dir, "metadata.json")
        with open(clip_json_path, 'r') as f:
            clip_data = json.load(f)
            clip_data['filtered_anno'] = self.filtered_annos
        with open(clip_json_path, 'w') as f:
            json.dump(clip_data, f)
        self.labeled_flag = True
     
    def run_tracker(self, configs):
        # not implement
        pass
    
    def run_blinker(self, configs):
        # not implement
        pass
    
    
    @staticmethod
    def color_name2color(color_name):
        color_dict = {'red':(255, 0, 0, 255),
                      'green':(0, 255, 0, 255),
                      'yellow':(255, 255, 0, 255),
                      'black':(255, 255, 255, 255),
                      'uncertain':(128, 128, 128, 255)}
        if color_name in color_dict:
            return color_dict[color_name]
        else:
            raise ValueError("Unknown class name: {}".format(color_name))

class BBOX:
    def __init__(self, bbox_anno):
        self.bbox_id = bbox_anno['bbox_id']
        self.ltrb = bbox_anno['bbox']
        self.det_confidence = bbox_anno['det_confidence']
        
        self.color_name = bbox_anno['attr']['color']
        self.installationType = bbox_anno['attr']['installationType']
        self.blink_state = bbox_anno['attr']['blink_state']
        self.track_id = bbox_anno['attr']['track_id']
    
    @staticmethod
    def set_bbox_anno(bbox_anno, bbox):
        bbox_anno['bbox'] = bbox.ltrb
        bbox_anno['attr']['color'] = bbox.color_name
        bbox_anno['attr']['installationType'] = bbox.installationType
        bbox_anno['attr']['blink_state'] = bbox.blink_state
        bbox_anno['attr']['track_id'] = bbox.track_id

class CLIP(CLIP_Base):
    def run_tracker(self, configs):
        tracker = BYTETracker(configs)
        annos_update = self.annos.copy()
        for anno in tqdm(annos_update, total=len(annos_update), desc=f"Processing Tracker..."):
            bboxes_anno = anno['bboxes_anno']
            dets = []
            ids = []
            for bbox_anno in bboxes_anno:
                bbox = bbox_anno['bbox']
                det = [bbox[0], bbox[1], bbox[2], bbox[3], bbox_anno['det_confidence'], bbox_anno['bbox_id']]
                dets.append(det)
                ids.append(bbox_anno['bbox_id'])
            dets = np.array(dets)
            
            # Update tracker
            info_imgs = (1080, 1920)  # Use provided image size
            img_size = (1080, 1920)  # Set your preprocessed image size here
            online_targets = tracker.update(dets, info_imgs, img_size)

            # Save tracking results
            for target in online_targets:
                target_bbox_id = target.bbox_id
                if target.state == TrackState.Tracked:
                    target_track_id = target.track_id
                elif target.state == TrackState.Lost:
                    target_track_id = -1
                    continue # lost target's bbox_id is unkonwn.
                if not target_bbox_id in ids:
                    raise Exception(f"target_bbox_id {target_bbox_id} not in ids {ids}")
                for bbox_anno in bboxes_anno:
                    if bbox_anno['bbox_id'] == target_bbox_id:
                        bbox_anno["attr"]['track_id'] = target_track_id
                        break
                ids.remove(target_bbox_id)
            # unmatched bboxes's track_id is -1
            if len(ids) > 0:
                for bbox_anno in bboxes_anno:
                    if bbox_anno['bbox_id'] in ids:
                        bbox_anno["attr"]['track_id'] = -1
                        
        self.annos = annos_update
    
    def run_blinker(self):
        # color options: ["red", "green", "yellow", "black", "uncertain"]
        # blink_states 
        annos = self.filtered_annos
        filtered_tracking_info = self.filtered_tracking_info.copy()
        for track_info in filtered_tracking_info:
            start_frame = track_info['start_frame']-1
            end_frame = track_info['end_frame']-1
            track_id = track_info['id']
            history_colors = "black"
            blink_state = "no_blink"
            blink_count = 0
            for frame_annos in annos[start_frame:end_frame+1]:
                for bbox_anno in frame_annos['bboxes_anno']:
                    if bbox_anno['attr']['track_id']==track_id:
                        current_color = bbox_anno['attr']['color']
                        if history_colors in ["green"] and current_color=="uncertain":
                            blink_state = "blink"
                        elif current_color in ["red", "yellow"]:
                            blink_state = "no_blink"
                        elif current_color=="green" and blink_count<4: # 绿灯时很快的闪了一下
                            blink_state = "no_blink"
                        else: # 需不需要blink_count达到一定帧数才算作blink
                            pass # no change
                        if not blink_state:
                            print("aaaaaaaaaaaaaaaaaaa")
                        bbox_anno['attr']['blink_state'] = blink_state
                        history_colors = current_color
                        if blink_state=="blink":
                            blink_count += 1
                        else:
                            blink_count = 0
