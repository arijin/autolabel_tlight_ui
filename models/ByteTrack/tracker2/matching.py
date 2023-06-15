import numpy as np
import scipy
import lap
import math
from scipy.spatial.distance import cdist

from . import kalman_filter
import time

def merge_matches(m1, m2, shape):
    O,P,Q = shape
    m1 = np.asarray(m1)
    m2 = np.asarray(m2)

    M1 = scipy.sparse.coo_matrix((np.ones(len(m1)), (m1[:, 0], m1[:, 1])), shape=(O, P))
    M2 = scipy.sparse.coo_matrix((np.ones(len(m2)), (m2[:, 0], m2[:, 1])), shape=(P, Q))

    mask = M1*M2
    match = mask.nonzero()
    match = list(zip(match[0], match[1]))
    unmatched_O = tuple(set(range(O)) - set([i for i, j in match]))
    unmatched_Q = tuple(set(range(Q)) - set([j for i, j in match]))

    return match, unmatched_O, unmatched_Q


def _indices_to_matches(cost_matrix, indices, thresh):
    matched_cost = cost_matrix[tuple(zip(*indices))]
    matched_mask = (matched_cost <= thresh)

    matches = indices[matched_mask]
    unmatched_a = tuple(set(range(cost_matrix.shape[0])) - set(matches[:, 0]))
    unmatched_b = tuple(set(range(cost_matrix.shape[1])) - set(matches[:, 1]))

    return matches, unmatched_a, unmatched_b


def linear_assignment(cost_matrix, thresh):
    if cost_matrix.size == 0:
        return np.empty((0, 2), dtype=int), tuple(range(cost_matrix.shape[0])), tuple(range(cost_matrix.shape[1]))
    matches, unmatched_a, unmatched_b = [], [], []
    cost, x, y = lap.lapjv(cost_matrix, extend_cost=True, cost_limit=thresh)
    for ix, mx in enumerate(x):
        if mx >= 0:
            matches.append([ix, mx])
    unmatched_a = np.where(x < 0)[0]
    unmatched_b = np.where(y < 0)[0]
    matches = np.asarray(matches)
    return matches, unmatched_a, unmatched_b

def id_switch(matches, detections, strack_pool):
    if (len(detections) > 0 and isinstance(detections[0], np.ndarray)):
        detections = detections
    else:
        detections = [track.tlwh_to_tlbr(track.pred_bbox) for track in detections]
    strack_pool = [track.track_id for track in strack_pool]
    
    centers = list()
    widths = list()
    heights = list()
    for det in detections:
        centers.append(((det[0] + det[2]) / 2, (det[1] + det[3]) / 2))
        widths.append(det[2] - det[0])
        heights.append(det[3] - det[1])
        
    def switch(id_a, id_b):
        if (id_a[1] > id_b[1] and centers[id_a[2]][0] < centers[id_b[2]][0]) or (id_a[1] < id_b[1] and centers[id_a[2]][0] > centers[id_b[2]][0]):
            matches[id_a[0]][1] = id_b[2]
            matches[id_b[0]][1] = id_a[2]
            
    groups = list()
    for i, match in enumerate(matches):
        itracked, idet = match
        itracked_id = strack_pool[itracked]
        center = centers[idet]
        flag = False
        for group in groups:
            for j, track_id, id in group:
                if itracked_id in [2, 3] and track_id in [2, 3]:
                    print("aaa")
                if abs(center[0] - centers[id][0]) < widths[id] * 5 and abs(center[1] - centers[id][1]) < heights[id] * 0.5:
                    group.append((i, itracked, idet))
                    switch((i, itracked_id, idet), (j, track_id, id))
                    flag = True
                    break
            if flag:
                break
        if not flag:
            groups.append([(i, itracked_id, idet)])
    
    return matches

def resort_undetection(u_detection, detections):
    if (len(detections) > 0 and isinstance(detections[0], np.ndarray)):
        detections = detections
    else:
        detections = [track.tlwh_to_tlbr(track.pred_bbox) for track in detections]
    centers = list()
    for det in detections:
        centers.append(((det[0] + det[2]) / 2, (det[1] + det[3]) / 2))
    return sorted(u_detection, key=lambda idx: centers[idx][0])

def calculate_iou(a, b):
    # 计算IoU
    inter_area = max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))
    a_area = (a[2] - a[0]) * (a[3] - a[1])
    b_area = (b[2] - b[0]) * (b[3] - b[1])
    union_area = a_area + b_area - inter_area
    iou = inter_area / (union_area + 1e-6)
    return iou

def iou_distance(atracks, btracks):
    """
    Compute cost based on IoU
    :type atracks: list[STrack]
    :type btracks: list[STrack]

    :rtype cost_matrix np.ndarray
    """

    if (len(atracks)>0 and isinstance(atracks[0], np.ndarray)) or (len(btracks) > 0 and isinstance(btracks[0], np.ndarray)):
        atlbrs = atracks
        btlbrs = btracks
    else:
        atlbrs = [track.tlbr for track in atracks]
        btlbrs = [track.tlbr for track in btracks]
        
    num_atracks = len(atlbrs)
    num_btracks = len(btlbrs)
    cost_matrix = np.zeros((num_atracks, num_btracks), dtype=np.float32)
    for i, a in enumerate(atlbrs):
        for j, b in enumerate(btlbrs):
            iou = calculate_iou(a, b)
            cost_matrix[i, j] = 1 - iou

    return cost_matrix

def v_iou_distance(atracks, btracks):
    """
    Compute cost based on IoU
    :type atracks: list[STrack]
    :type btracks: list[STrack]

    :rtype cost_matrix np.ndarray
    """

    if (len(atracks)>0 and isinstance(atracks[0], np.ndarray)) or (len(btracks) > 0 and isinstance(btracks[0], np.ndarray)):
        atlbrs = atracks
        btlbrs = btracks
    else:
        atlbrs = [track.tlwh_to_tlbr(track.pred_bbox) for track in atracks]
        btlbrs = [track.tlwh_to_tlbr(track.pred_bbox) for track in btracks]
    num_atracks = len(atlbrs)
    num_btracks = len(btlbrs)
    cost_matrix = np.zeros((num_atracks, num_btracks), dtype=np.float32)
    for i, a in enumerate(atlbrs):
        for j, b in enumerate(btlbrs):
            iou = calculate_iou(a, b)
            cost_matrix[i, j] = 1 - iou

    return cost_matrix

def calculate_diou(a, b):
    # 计算IoU
    inter_area = max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))
    a_area = (a[2] - a[0]) * (a[3] - a[1])
    b_area = (b[2] - b[0]) * (b[3] - b[1])
    union_area = a_area + b_area - inter_area
    iou = inter_area / union_area
    # 计算中心点距离
    a_center = [(a[0] + a[2]) / 2, (a[1] + a[3]) / 2]
    b_center = [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2]
    center_distance = np.sqrt((a_center[0] - b_center[0])**2 + (a_center[1] - b_center[1])**2)
    # 计算对角线距离
    diag_length = np.sqrt((a[2] - a[0])**2 + (a[3] - a[1])**2) + np.sqrt((b[2] - b[0])**2 + (b[3] - b[1])**2)
    width_c = max(a[2], b[2]) - min(a[0], b[0])
    height_c = max(a[3], b[3]) - min(a[1], b[1])
    diag_length_square = np.sqrt(width_c ** 2 + height_c ** 2)
    # 计算DIoU
    diou = iou + (1 - center_distance / diag_length_square) # (0, 2), miner farther, cost smaller
    return diou

def diou_distance(atracks, btracks):
    """
    Compute cost based on DIoU
    :type atracks: list[STrack]
    :type btracks: list[STrack]

    :rtype cost_matrix np.ndarray
    """
    if (len(atracks) > 0 and isinstance(atracks[0], np.ndarray)) or (len(btracks) > 0 and isinstance(btracks[0], np.ndarray)):
        atlbrs = atracks
        btlbrs = btracks
    else:
        atlbrs = [track.tlbr for track in atracks]
        btlbrs = [track.tlbr for track in btracks]

    num_atracks = len(atlbrs)
    num_btracks = len(btlbrs)
    cost_matrix = np.zeros((num_atracks, num_btracks), dtype=np.float32)
    for i, a in enumerate(atlbrs):
        for j, b in enumerate(btlbrs):
            diou = calculate_diou(a, b)
            cost_matrix[i, j] = (2 - diou)/2.0

    return cost_matrix

def v_diou_distance(atracks, btracks):
    """
    Compute cost based on DIoU
    :type atracks: list[STrack]
    :type btracks: list[STrack]

    :rtype cost_matrix np.ndarray
    """
    if (len(atracks) > 0 and isinstance(atracks[0], np.ndarray)) or (len(btracks) > 0 and isinstance(btracks[0], np.ndarray)):
        atlbrs = atracks
        btlbrs = btracks
    else:
        atlbrs = [track.tlwh_to_tlbr(track.pred_bbox) for track in atracks]
        btlbrs = [track.tlwh_to_tlbr(track.pred_bbox) for track in btracks]

    num_atracks = len(atlbrs)
    num_btracks = len(btlbrs)
    cost_matrix = np.zeros((num_atracks, num_btracks), dtype=np.float32)
    for i, a in enumerate(atlbrs):
        for j, b in enumerate(btlbrs):
            diou = calculate_diou(a, b)
            cost_matrix[i, j] = (2 - diou)/2.0

    return cost_matrix

def center_distance(atracks, btracks, max_distance):
    """
    Compute cost based on DIoU
    :type atracks: list[STrack]
    :type btracks: list[STrack]

    :rtype cost_matrix np.ndarray
    """
    if (len(atracks) > 0 and isinstance(atracks[0], np.ndarray)) or (len(btracks) > 0 and isinstance(btracks[0], np.ndarray)):
        atlbrs = atracks
        btlbrs = btracks
    else:
        atlbrs = [track.tlbr for track in atracks]
        btlbrs = [track.tlbr for track in btracks]

    num_atracks = len(atlbrs)
    num_btracks = len(btlbrs)
    cost_matrix = np.zeros((num_atracks, num_btracks), dtype=np.float32)
    for i, a in enumerate(atlbrs):
        for j, b in enumerate(btlbrs):
            a_center = [(a[0] + a[2]) / 2, (a[1] + a[3]) / 2]
            b_center = [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2]
            center_distance = np.sqrt((a_center[0] - b_center[0])**2 + (a_center[1] - b_center[1])**2)
            wa, ha = a[2] - a[0], a[3] - a[1]
            wb, hb = b[2] - b[0], b[3] - b[1]
            # scale_distance = 1 - min((wa * ha) / (wb * hb), (wb * hb) / (wa * ha))
            scale_distance = ((wa * ha) - (wb * hb)) ** 2
            cost_matrix[i, j] = scale_distance

    return cost_matrix

def v_center_distance(atracks, btracks, max_distance):
    """
    Compute cost based on DIoU
    :type atracks: list[STrack]
    :type btracks: list[STrack]

    :rtype cost_matrix np.ndarray
    """
    if (len(atracks) > 0 and isinstance(atracks[0], np.ndarray)) or (len(btracks) > 0 and isinstance(btracks[0], np.ndarray)):
        atlbrs = atracks
        btlbrs = btracks
    else:
        atlbrs = [track.tlwh_to_tlbr(track.pred_bbox) for track in atracks]
        btlbrs = [track.tlwh_to_tlbr(track.pred_bbox) for track in btracks]

    num_atracks = len(atlbrs)
    num_btracks = len(btlbrs)
    cost_matrix = np.zeros((num_atracks, num_btracks), dtype=np.float32)
    for i, a in enumerate(atlbrs):
        for j, b in enumerate(btlbrs):
            a_center = [(a[0] + a[2]) / 2, (a[1] + a[3]) / 2]
            b_center = [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2]
            x_shift= a_center[0] - b_center[0]
            y_shift= a_center[1] - b_center[1]
            center_distance = np.sqrt((a_center[0] - b_center[0])**2 + (a_center[1] - b_center[1])**2)
            wa, ha = a[2] - a[0], a[3] - a[1]
            wb, hb = b[2] - b[0], b[3] - b[1]
            # scale_distance = 1 - min((wa * ha) / (wb * hb), (wb * hb) / (wa * ha))
            scale_distance = max(((wa * ha) - (wb * hb)) ** 2, 1000) / 1000
            cost_matrix[i, j] = 1 * min(center_distance, max_distance)/(max_distance*1.0)

    return cost_matrix

def embedding_distance(tracks, detections, metric='cosine'):
    """
    :param tracks: list[STrack]
    :param detections: list[BaseTrack]
    :param metric:
    :return: cost_matrix np.ndarray
    """

    cost_matrix = np.zeros((len(tracks), len(detections)), dtype=np.float)
    if cost_matrix.size == 0:
        return cost_matrix
    det_features = np.asarray([track.curr_feat for track in detections], dtype=np.float)
    #for i, track in enumerate(tracks):
        #cost_matrix[i, :] = np.maximum(0.0, cdist(track.smooth_feat.reshape(1,-1), det_features, metric))
    track_features = np.asarray([track.smooth_feat for track in tracks], dtype=np.float)
    cost_matrix = np.maximum(0.0, cdist(track_features, det_features, metric))  # Nomalized features
    return cost_matrix


def gate_cost_matrix(kf, cost_matrix, tracks, detections, only_position=False):
    if cost_matrix.size == 0:
        return cost_matrix
    gating_dim = 2 if only_position else 4
    gating_threshold = kalman_filter.chi2inv95[gating_dim]
    measurements = np.asarray([det.to_xyah() for det in detections])
    for row, track in enumerate(tracks):
        gating_distance = kf.gating_distance(
            track.mean, track.covariance, measurements, only_position)
        cost_matrix[row, gating_distance > gating_threshold] = np.inf
    return cost_matrix


def fuse_motion(kf, cost_matrix, tracks, detections, only_position=False, lambda_=1):
    if cost_matrix.size == 0:
        return cost_matrix
    gating_dim = 2 if only_position else 4
    gating_threshold = kalman_filter.chi2inv95[gating_dim]
    measurements = np.asarray([det.to_xyah() for det in detections])
    for row, track in enumerate(tracks):
        gating_distance = kf.gating_distance(
            track.mean, track.covariance, measurements, only_position, metric='maha')
        cost_matrix[row, gating_distance > gating_threshold] = np.inf
        cost_matrix[row] = lambda_ * cost_matrix[row] + (1 - lambda_) * gating_distance
    return cost_matrix

def fuse_lost_track(cost_matrix, tracks):
    if cost_matrix.size == 0:
        return cost_matrix
    fuse_sim = 1 - cost_matrix
    for row, track in enumerate(tracks):
        lost_frames = track.lost_frames
        lost_weight = 1 - min(lost_frames, 5) / 10.0
        fuse_sim[row] = lost_weight * fuse_sim[row]
    fuse_cost = 1 - fuse_sim
    return fuse_cost

def fuse_iou(cost_matrix, tracks, detections, lambda_=1):
    if cost_matrix.size == 0:
        return cost_matrix
    reid_sim = 1 - cost_matrix
    iou_dist = iou_distance(tracks, detections)
    iou_sim = 1 - iou_dist
    fuse_sim = lambda_*reid_sim + (1-lambda_)*iou_sim
    det_scores = np.array([det.score for det in detections])
    det_scores = np.expand_dims(det_scores, axis=0).repeat(cost_matrix.shape[0], axis=0)
    #fuse_sim = fuse_sim * (1 + det_scores) / 2
    fuse_cost = 1 - fuse_sim
    return fuse_cost


def fuse_score(cost_matrix, detections):
    if cost_matrix.size == 0:
        return cost_matrix
    iou_sim = 1 - cost_matrix
    det_scores = np.array([det.score for det in detections])
    det_scores = np.expand_dims(det_scores, axis=0).repeat(cost_matrix.shape[0], axis=0)
    fuse_sim = iou_sim * det_scores
    fuse_cost = 1 - fuse_sim
    return fuse_cost

