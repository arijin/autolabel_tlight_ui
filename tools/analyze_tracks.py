# import os
# import json
# from collections import defaultdict

# def analyze_tracking_results(folder_name):
#     # 获取文件夹中的所有txt文件并排序
#     txt_files = sorted([f for f in os.listdir(folder_name) if f.endswith('.txt')])

#     # 初始化字典存储跟踪信息
#     tracking_info = defaultdict(lambda: {'start_frame': None, 'end_frame': None, 'frame_count': 0, 'total_confidence': 0.0})

#     # 遍历每个文件并解析跟踪结果
#     for frame_idx, txt_file in enumerate(txt_files):
#         with open(os.path.join(folder_name, txt_file), 'r') as f:
#             for line in f.readlines():
#                 id, min_x, min_y, max_x, max_y, confidence = line.strip().split()
#                 id, confidence = int(id), float(confidence)

#                 # 更新跟踪信息
#                 if tracking_info[id]['start_frame'] is None:
#                     tracking_info[id]['start_frame'] = frame_idx + 1
#                 tracking_info[id]['end_frame'] = frame_idx + 1
#                 tracking_info[id]['frame_count'] += 1
#                 tracking_info[id]['total_confidence'] += confidence

#     # 计算平均confidence并整理输出结果
#     summary = []
#     for id, info in tracking_info.items():
#         avg_confidence = info['total_confidence'] / info['frame_count']
#         summary.append((id, info['start_frame'], info['end_frame'], info['frame_count'], avg_confidence))

#     # 计算平均confidence并整理输出结果
#     summary = []
#     for id, info in tracking_info.items():
#         avg_confidence = info['total_confidence'] / info['frame_count']
#         summary.append({'id': id, 'start_frame': info['start_frame'], 'end_frame': info['end_frame'], 'frame_count': info['frame_count'], 'average_confidence': round(avg_confidence, 2)})

#     # 输出结果到JSON文件
#     with open('summary.json', 'w') as f:
#         json.dump(summary, f, indent=2)

#     return summary

# folder_name = 'clip'
# analyze_tracking_results(folder_name)





import os
import json
from collections import defaultdict

def analyze_tracking_results(folder_name):
    # 获取文件夹中的所有txt文件并排序
    txt_files = sorted([f for f in os.listdir(folder_name) if f.endswith('.txt') and (not f=="log.txt")])

    # 初始化字典存储跟踪信息
    tracking_info = defaultdict(lambda: {'start_frame': None, 'end_frame': None, 'start_frame_name': None, 'end_frame_name': None, 'frame_count': 0, 'total_confidence': 0.0, 'lost_frames': []})

    # 遍历每个文件并解析跟踪结果
    for frame_idx, txt_file in enumerate(txt_files):
        with open(os.path.join(folder_name, txt_file), 'r') as f:
            for line in f.readlines():
                id, min_x, min_y, max_x, max_y, confidence = line.strip().split()
                id, confidence = int(id), float(confidence)
                min_x, min_y, max_x, max_y = float(min_x), float(min_y), float(max_x), float(max_y)

                # 检查是否有坐标为-1，如有则添加帧索引到该物体的lost_frames列表
                if -1 in [min_x, min_y, max_x, max_y]:
                    if frame_idx + 1 not in tracking_info[id]['lost_frames']:
                        tracking_info[id]['lost_frames'].append(frame_idx + 1)

                # 更新跟踪信息
                if tracking_info[id]['start_frame'] is None:
                    tracking_info[id]['start_frame'] = frame_idx + 1
                    tracking_info[id]['start_frame_name'] = txt_file
                tracking_info[id]['end_frame'] = frame_idx + 1
                tracking_info[id]['end_frame_name'] = txt_file
                tracking_info[id]['frame_count'] += 1
                tracking_info[id]['total_confidence'] += confidence

    # 计算平均confidence并整理输出结果
    summary = {'objects': []}
    for id, info in tracking_info.items():
        avg_confidence = info['total_confidence'] / info['frame_count']
        summary['objects'].append({'id': id, 'start_frame': info['start_frame'], 'end_frame': info['end_frame'], 'start_frame_name': info['start_frame_name'], 'end_frame_name': info['end_frame_name'], 'frame_count': info['frame_count'], 'average_confidence': round(avg_confidence, 2), 'lost_frames': info['lost_frames']})

    # 输出结果到JSON文件
    with open(os.path.join(folder_name, 'summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)

    return summary

tracks_dir = r"C:\Users\qj00241.7HORSE\Downloads\MLT\tl_tracks\dishui_lake_1"
analyze_tracking_results(tracks_dir)
