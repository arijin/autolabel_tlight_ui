import numpy as np
from collections import deque
import os
import os.path as osp
import copy

from .kalman_filter import KalmanFilter
from . import matching
from .basetrack import BaseTrack, TrackState

class STrack(BaseTrack):
    shared_kalman = KalmanFilter()
    def __init__(self, tlwh, score, bbox_id):
        """初始化 STrack 类。

        Args:
            tlwh: numpy.ndarray, 边界框 (shape: [4])。
            score: float, 目标的置信度得分。
        """
        # wait activate
        self._tlwh = np.asarray(tlwh, dtype=np.float)
        self._det_tlbr = self.tlwh_to_tlbr(self._tlwh)
        self.kalman_filter = None
        self.mean, self.covariance = None, None
        self.is_activated = False

        self._bbox_id = bbox_id
        self.score = score
        self.tracklet_len = 0
        

    def predict(self):
        """预测目标的下一个状态。"""
        mean_state = self.mean.copy()
        if self.state != TrackState.Tracked:
            mean_state[7] = 0
        self.mean, self.covariance = self.kalman_filter.predict(mean_state, self.covariance)

    @staticmethod
    def multi_predict(stracks):
        """批量预测多个目标的下一个状态。

        Args:
            stracks: list, STrack对象列表。
        """
        if len(stracks) > 0:
            multi_mean = np.asarray([st.mean.copy() for st in stracks])
            multi_covariance = np.asarray([st.covariance for st in stracks])
            for i, st in enumerate(stracks):
                if st.state != TrackState.Tracked:
                    multi_mean[i][7] = 0
            multi_mean, multi_covariance = STrack.shared_kalman.multi_predict(multi_mean, multi_covariance)
            for i, (mean, cov) in enumerate(zip(multi_mean, multi_covariance)):
                stracks[i].mean = mean
                stracks[i].covariance = cov

    def activate(self, kalman_filter, frame_id):
        """激活一个新的轨迹。Start a new tracklet

        Args:
            kalman_filter: KalmanFilter对象，用于目标状态估计。
            frame_id: int, 当前帧编号。
        """
        self.kalman_filter = kalman_filter
        self.track_id = self.next_id()
        # print("aaa", self.bbox_id, self.track_id)
        self.mean, self.covariance = self.kalman_filter.initiate(self.tlwh_to_xyah(self._tlwh))

        self.tracklet_len = 0
        self.state = TrackState.Tracked
        # if frame_id == 1:
        #     self.is_activated = True
        self.is_activated = True # 非第一帧只有被看到两次才会被激活
        self.frame_id = frame_id
        # self.lost_frames = 0
        self.minus_lost_frames()
        self.start_frame = frame_id

    def re_activate(self, new_track, frame_id, new_id=False):
        """重新激活一个轨迹。

        Args:
            new_track: STrack对象，新的目标。
            frame_id: int, 当前帧编号。
            new_id: bool, optional, 默认值: False。是否为重新激活的轨迹分配一个新ID。
        """
        new_tlwh = new_track.tlwh
        self.mean, self.covariance = self.kalman_filter.update(
            self.mean, self.covariance, self.tlwh_to_xyah(new_tlwh)
        )
        self._det_tlbr = self.tlwh_to_tlbr(new_tlwh)
        self.tracklet_len = 0
        self.state = TrackState.Tracked
        self.is_activated = True
        self.frame_id = frame_id
        # self.lost_frames = 0
        self.minus_lost_frames()
        if new_id:
            self.track_id = self.next_id()
        self.score = new_track.score
        self._bbox_id = new_track._bbox_id

    def update(self, new_track, frame_id):
        """更新匹配的轨迹。Update a matched track.

        Args:
            new_track: STrack对象，新的目标。
            frame_id: int, 当前帧编号。
            # type update_feature: bool
            return:
        """
        self.frame_id = frame_id
        self.tracklet_len += 1

        new_tlwh = new_track.tlwh
        self.mean, self.covariance = self.kalman_filter.update(
            self.mean, self.covariance, self.tlwh_to_xyah(new_tlwh))
        self._det_tlbr = self.tlwh_to_tlbr(new_tlwh)
        self.state = TrackState.Tracked
        self.is_activated = True

        self.score = new_track.score
        self._bbox_id = new_track._bbox_id

    @property
    # @jit(nopython=True)
    def bbox_id(self):
        """获取当前目标的ID。"""
        return self._bbox_id

    @property
    # @jit(nopython=True)
    def det_tlbr(self):
        """获取当前最新det位置的边界框格式 (top left x, top left y, width, height)。"""
        return self._det_tlbr.copy()

    @property
    # @jit(nopython=True)
    def pred_bbox(self):
        """获取当前位置的边界框格式 (top left x, top left y, width, height)。"""
        if self.mean is None:
            return self._tlwh.copy()
        mean_state = self.mean.copy()
        if self.state != TrackState.Tracked:
            mean_state[7] = 0
        mean, _ = self.kalman_filter.predict(mean_state, self.covariance)
        ret = mean[:4].copy()
        ret[2] *= ret[3]
        ret[:2] -= ret[2:] / 2
        return ret

    @property
    # @jit(nopython=True)
    def tlwh(self):
        """获取当前位置的边界框格式 (top left x, top left y, width, height)。"""
        if self.mean is None:
            return self._tlwh.copy()
        ret = self.mean[:4].copy()
        ret[2] *= ret[3]
        ret[:2] -= ret[2:] / 2
        return ret

    @property
    # @jit(nopython=True)
    def tlbr(self):
        """将边界框转换为格式 (min x, min y, max x, max y)，即 (left, top, right, bottom)。"""
        ret = self.tlwh.copy()
        ret[2:] += ret[:2]
        return ret

    @staticmethod
    # @jit(nopython=True)
    def tlwh_to_xyah(tlwh):
        """将边界框转换为格式 (center x, center y, aspect ratio, height)，其中宽高比为 width / height。

        Args:
            tlwh: numpy.ndarray, 边界框 (shape: [4])。

        Returns:
            ret: numpy.ndarray, 转换后的表示 (shape: [4])。
        """
        ret = np.asarray(tlwh).copy()
        ret[:2] += ret[2:] / 2
        ret[2] /= ret[3]
        return ret

    def to_xyah(self):
        """将当前目标的边界框转换为 (center x, center y, aspect ratio, height) 格式。"""
        return self.tlwh_to_xyah(self.tlwh)

    @staticmethod
    # @jit(nopython=True)
    def tlbr_to_tlwh(tlbr):
        """将边界框从格式 (min x, min y, max x, max y) 转换为格式 (top left x, top left y, width, height)。

        Args:
            tlbr: numpy.ndarray, 边界框 (shape: [4])。

        Returns:
            ret: numpy.ndarray, 转换后的表示 (shape: [4])。
        """
        ret = np.asarray(tlbr).copy()
        ret[2:] -= ret[:2]
        return ret

    @staticmethod
    # @jit(nopython=True)
    def tlwh_to_tlbr(tlwh):
        ret = np.asarray(tlwh).copy()
        ret[2:] += ret[:2]
        return ret

    def __repr__(self):
        return 'OT_{}_({}-{})'.format(self.track_id, self.start_frame, self.end_frame)


class BYTETracker(object):
    kf = KalmanFilter()
    def __init__(self, configs):
        """初始化 BYTETracker 类。

        Args:
            frame_rate: int, optional, 默认值: 30。视频帧率。
        """
        self.tracked_stracks = []  # type: list[STrack]
        self.lost_stracks = []  # type: list[STrack]
        self.removed_stracks = []  # type: list[STrack]

        self.frame_id = 0
        self.match_thresh = configs['match_thresh'] if configs['match_thresh'] else 0.99
        self.det_thresh = configs['det_thresh'] if configs['det_thresh'] else 0.3  # args.track_thresh + 0.1
        self.track_thresh = configs['track_thresh'] if configs['track_thresh'] else 0.3
        self.fuse_det_score = configs['fuse_det_score'] if configs['fuse_det_score'] else True
        self.max_distance = configs['max_distance'] if configs['max_distance'] else 100
        self.track_buffer = configs['track_buffer'] if configs['track_buffer'] else 4
        self.frame_rate = configs['frame_rate'] if configs['frame_rate'] else 30
        
        self.buffer_size = int(self.frame_rate / 30.0 * self.track_buffer)
        self.max_time_lost = self.buffer_size
        self.kalman_filter = KalmanFilter()
        BaseTrack._count = 0

    def update(self, output_results, img_info, img_size):
        """更新跟踪器状态。

        Args:
            output_results: numpy.ndarray, 检测到的边界框和分数 (shape: [num_detections, 4或5])。
            img_info: list or tuple, 原始图像的高度和宽度 (shape: [2])。
            img_size: list or tuple, 输入图像的高度和宽度 (shape: [2])。

        Returns:
            output_stracks: list, 已激活跟踪目标列表，每个元素为STrack实例。
        """
        self.frame_id += 1
        activated_starcks = []
        refind_stracks = []
        lost_stracks = []
        removed_stracks = []

        if len(output_results)>0:
            if output_results.shape[1] == 6:
                scores = output_results[:, 4]
                bboxes = output_results[:, :4]
                ids = output_results[:, 5]
            else:
                output_results = output_results.cpu().numpy()
                scores = output_results[:, 4] * output_results[:, 5]
                bboxes = output_results[:, :4]  # x1y1x2y2
                ids = output_results[:, 6]
            img_h, img_w = img_info[0], img_info[1]
            scale = min(img_size[0] / float(img_h), img_size[1] / float(img_w))
            bboxes /= scale

            remain_inds = scores > self.track_thresh
            inds_low = scores > 0.1
            inds_high = scores < self.track_thresh

            inds_second = np.logical_and(inds_low, inds_high)
            dets_second = bboxes[inds_second]
            dets = bboxes[remain_inds]
            dets_id_second = ids[inds_second]
            dets_id = ids[remain_inds]
            scores_keep = scores[remain_inds]
            scores_second = scores[inds_second]
        else:
            dets_second = []
            dets = []
            dets_id = []
            scores_keep = []
            scores_second = []

        if len(dets) > 0:
            '''Detections'''
            detections = [STrack(STrack.tlbr_to_tlwh(tlbr), s, id) for
                          (tlbr, s, id) in zip(dets, scores_keep, dets_id)]
        else:
            detections = []

        ''' Add newly detected tracklets to tracked_stracks'''
        unconfirmed = []
        tracked_stracks = []  # type: list[STrack]
        for track in self.tracked_stracks:
            if not track.is_activated:
                unconfirmed.append(track)
            else:
                tracked_stracks.append(track)

        ''' Step 2: First association, with high score detection boxes'''
        strack_pool = joint_stracks(tracked_stracks, self.lost_stracks)
        # Predict the current location with KF
        STrack.multi_predict(strack_pool)
        dists = matching.v_center_distance(strack_pool, detections, self.max_distance) # v_iou_distance v_diou_distance
        if self.fuse_det_score:
            dists = matching.fuse_score(dists, detections)
            dists = matching.fuse_iou(dists, strack_pool, detections, lambda_=1)
            dists = matching.fuse_lost_track(dists, strack_pool)
            # dists = matching.fuse_motion(self.kf, dists, strack_pool, detections, lambda_=1)
        matches, u_track, u_detection = matching.linear_assignment(dists, thresh=self.match_thresh)
        matches = matching.id_switch(matches, detections, strack_pool)

        for itracked, idet in matches:
            track = strack_pool[itracked]
            det = detections[idet]
            if track.state == TrackState.Tracked:
                track.update(detections[idet], self.frame_id)
                activated_starcks.append(track)
            else:
                track.re_activate(det, self.frame_id, new_id=False)
                refind_stracks.append(track)

        ''' Step 3: Second association, with low score detection boxes'''
        # association the untrack to the low score detections
        if len(dets_second) > 0:
            '''Detections'''
            detections_second = [STrack(STrack.tlbr_to_tlwh(tlbr), s, id) for
                          (tlbr, s, id) in zip(dets_second, scores_second, dets_id_second)]
        else:
            detections_second = []
        r_tracked_stracks = [strack_pool[i] for i in u_track if strack_pool[i].state == TrackState.Tracked]
        dists = matching.iou_distance(r_tracked_stracks, detections_second)
        matches, u_track, u_detection_second = matching.linear_assignment(dists, thresh=0.5)
        for itracked, idet in matches:
            track = r_tracked_stracks[itracked]
            det = detections_second[idet]
            if track.state == TrackState.Tracked:
                track.update(det, self.frame_id)
                activated_starcks.append(track)
            else:
                track.re_activate(det, self.frame_id, new_id=False)
                refind_stracks.append(track)

        for it in u_track:
            track = r_tracked_stracks[it]
            if not track.state == TrackState.Lost:
                track.mark_lost()
                lost_stracks.append(track)

        '''Deal with unconfirmed tracks, usually tracks with only one beginning frame'''
        detections = [detections[i] for i in u_detection]
        dists = matching.iou_distance(unconfirmed, detections)
        if not self.fuse_det_score:
            dists = matching.fuse_score(dists, detections)
        matches, u_unconfirmed, u_detection = matching.linear_assignment(dists, thresh=0.7)
        for itracked, idet in matches:
            unconfirmed[itracked].update(detections[idet], self.frame_id)
            activated_starcks.append(unconfirmed[itracked])
        for it in u_unconfirmed:
            track = unconfirmed[it]
            track.mark_removed()
            removed_stracks.append(track)

        """ Step 4: Init new stracks"""
        u_detection = matching.resort_undetection(u_detection, detections)
        for inew in u_detection:
            track = detections[inew]
            if track.score < self.det_thresh:
                continue
            track.activate(self.kalman_filter, self.frame_id)
            activated_starcks.append(track)
        """ Step 5: Update state"""
        for track in self.lost_stracks:
            if self.frame_id - track.end_frame > self.max_time_lost:
                track.mark_removed()
                removed_stracks.append(track)
            else:
                track.add_lost_frames()

        # print('Ramained match {} s'.format(t4-t3))

        self.tracked_stracks = [t for t in self.tracked_stracks if t.state == TrackState.Tracked]
        self.tracked_stracks = joint_stracks(self.tracked_stracks, activated_starcks)
        self.tracked_stracks = joint_stracks(self.tracked_stracks, refind_stracks)
        self.lost_stracks = sub_stracks(self.lost_stracks, self.tracked_stracks)
        self.lost_stracks.extend(lost_stracks)
        self.lost_stracks = sub_stracks(self.lost_stracks, self.removed_stracks)
        self.removed_stracks.extend(removed_stracks)
        self.tracked_stracks, self.lost_stracks = remove_duplicate_stracks(self.tracked_stracks, self.lost_stracks)
        # get scores of lost tracks
        output_stracks = [track for track in self.tracked_stracks if track.is_activated]

        return output_stracks


def joint_stracks(tlista, tlistb):
    exists = {}
    res = []
    for t in tlista:
        exists[t.track_id] = 1
        res.append(t)
    for t in tlistb:
        tid = t.track_id
        if not exists.get(tid, 0):
            exists[tid] = 1
            res.append(t)
    return res


def sub_stracks(tlista, tlistb):
    stracks = {}
    for t in tlista:
        stracks[t.track_id] = t
    for t in tlistb:
        tid = t.track_id
        if stracks.get(tid, 0):
            del stracks[tid]
    return list(stracks.values())


def remove_duplicate_stracks(stracksa, stracksb):
    pdist = matching.iou_distance(stracksa, stracksb)
    pairs = np.where(pdist < 0.15)
    dupa, dupb = list(), list()
    for p, q in zip(*pairs):
        timep = stracksa[p].frame_id - stracksa[p].start_frame
        timeq = stracksb[q].frame_id - stracksb[q].start_frame
        if timep > timeq:
            dupb.append(q)
        else:
            dupa.append(p)
    resa = [t for i, t in enumerate(stracksa) if not i in dupa]
    resb = [t for i, t in enumerate(stracksb) if not i in dupb]
    return resa, resb
