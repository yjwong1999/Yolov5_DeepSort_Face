# vim: expandtab:ts=4:sw=4
from __future__ import absolute_import
import numpy as np
from . import kalman_filter
from . import linear_assignment
from . import iou_matching
from .track import Track

from scipy.spatial.distance import cdist


def cosine_distance(a, b):
    return 1 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
'''
# cos distance based on opensphere repo (not sure got bug ma)
import torch.nn.functional as F 
import torch   
def cosine_distance(feats):
    feats = F.normalize(feats, dim=1)
    feats0 = feats[0, :]
    feats1 = feats[1, :]
    dist = 1 - torch.sum(feats0 * feats1, dim=-1)
    return dist.tolist()
'''   

class Tracker:
    """
    This is the multi-target tracker.
    Parameters
    ----------
    metric : nn_matching.NearestNeighborDistanceMetric
        A distance metric for measurement-to-track association.
    max_age : int
        Maximum number of missed misses before a track is deleted.
    n_init : int
        Number of consecutive detections before the track is confirmed. The
        track state is set to `Deleted` if a miss occurs within the first
        `n_init` frames.
    Attributes
    ----------
    metric : nn_matching.NearestNeighborDistanceMetric
        The distance metric used for measurement to track association.
    max_age : int
        Maximum number of missed misses before a track is deleted.
    n_init : int
        Number of frames that a track remains in initialization phase.
    kf : kalman_filter.KalmanFilter
        A Kalman filter to filter target trajectories in image space.
    tracks : List[Track]
        The list of active tracks at the current time step.
    """
    GATING_THRESHOLD = np.sqrt(kalman_filter.chi2inv95[4])

    def __init__(self, metric, max_iou_distance=0.9, max_age=30, n_init=3, _lambda=0, global_id_feats=None):
        self.metric = metric
        self.max_iou_distance = max_iou_distance
        self.max_age = max_age
        self.n_init = n_init
        self._lambda = _lambda

        self.kf = kalman_filter.KalmanFilter()
        self.tracks = []
        self._next_id = 1
        
        if global_id_feats is None:
            global_id_feats = {}
        self.id_feats = global_id_feats

    def predict(self):
        """Propagate track state distributions one time step forward.

        This function should be called once every time step, before `update`.
        """
        for track in self.tracks:
            track.predict(self.kf)

    def increment_ages(self):
        for track in self.tracks:
            track.increment_age()
            track.mark_missed()

    def update(self, detections, classes):
        """Perform measurement update and track management.

        Parameters
        ----------
        detections : List[deep_sort.detection.Detection]
            A list of detections at the current time step.

        """
        # Run matching cascade.
        matches, unmatched_tracks, unmatched_detections = \
            self._match(detections)

        # Update track set.
        print(self.id_feats.keys())
        for track_idx, detection_idx in matches:
            self.tracks[track_idx].update(
                self.kf, detections[detection_idx], classes[detection_idx])
            #########################
            id_ = self.tracks[track_idx].track_id
            feat_ = detections[detection_idx].feature
            if len(self.id_feats.keys()) == 0:
                self.id_feats[id_] = feat_
            elif id_ not in self.id_feats.keys():
                all_feats = list(self.id_feats.values())
                cos_dist = [cosine_distance(feat_, all_feats[i]) for i in range(len(all_feats))]
                cos_dist = np.array(cos_dist)
                print('zzzzzzzzzzzzzzzzzzzzzzzzzzz', cos_dist)
                if np.min(cos_dist) > 0.3:
                    self.id_feats[id_] = feat_
                else:
                    self.tracks[track_idx].track_id = list(self.id_feats.keys())[np.argmin(cos_dist)]
            '''
            # for opensphere repo cos dist
            id_ = self.tracks[track_idx].track_id
            feat_ = torch.tensor([detections[detection_idx].feature])
            if len(self.id_feats.keys()) == 0:
                self.id_feats[id_] = feat_
            elif id_ not in self.id_feats.keys():
                all_feats = torch.tensor(np.concatenate(list(self.id_feats.values()), axis=0))
                n_feat_ = torch.tensor(np.concatenate([feat_] * len(all_feats)))
                print(all_feats.shape, n_feat_.shape)
                cos_dist = cosine_distance(torch.cat([all_feats, n_feat_], dim=0))
                cos_dist = np.array(cos_dist)
                print('zzzzzzzzzzzzzzzzzzzzzzzzzzz', cos_dist)
                if np.min(cos_dist) > 0.3:
                    self.id_feats[id_] = feat_
                else:
                    self.tracks[track_idx].track_id = list(self.id_feats.keys())[np.argmin(cos_dist)]
            '''
            #########################
        for track_idx in unmatched_tracks:
            self.tracks[track_idx].mark_missed()
        for detection_idx in unmatched_detections:
            self._initiate_track(detections[detection_idx], classes[detection_idx].item())
        self.tracks = [t for t in self.tracks if not t.is_deleted()]

        # Update distance metric.
        active_targets = [t.track_id for t in self.tracks if t.is_confirmed()]
        features, targets = [], []
        for track in self.tracks:
            if not track.is_confirmed():
                continue
            features += track.features
            targets += [track.track_id for _ in track.features]
            track.features = []
        self.metric.partial_fit(np.asarray(features), np.asarray(targets), active_targets)

    def _full_cost_metric(self, tracks, dets, track_indices, detection_indices):
        """
        This implements the full lambda-based cost-metric. However, in doing so, it disregards
        the possibility to gate the position only which is provided by
        linear_assignment.gate_cost_matrix(). Instead, I gate by everything.
        Note that the Mahalanobis distance is itself an unnormalised metric. Given the cosine
        distance being normalised, we employ a quick and dirty normalisation based on the
        threshold: that is, we divide the positional-cost by the gating threshold, thus ensuring
        that the valid values range 0-1.
        Note also that the authors work with the squared distance. I also sqrt this, so that it
        is more intuitive in terms of values.
        """
        # Compute First the Position-based Cost Matrix
        pos_cost = np.empty([len(track_indices), len(detection_indices)])
        msrs = np.asarray([dets[i].to_xyah() for i in detection_indices])
        for row, track_idx in enumerate(track_indices):
            pos_cost[row, :] = np.sqrt(
                self.kf.gating_distance(
                    tracks[track_idx].mean, tracks[track_idx].covariance, msrs, False
                )
            ) / self.GATING_THRESHOLD
        pos_gate = pos_cost > 1.0
        # Now Compute the Appearance-based Cost Matrix
        app_cost = self.metric.distance(
            np.array([dets[i].feature for i in detection_indices]),
            np.array([tracks[i].track_id for i in track_indices]),
        )
        app_gate = app_cost > self.metric.matching_threshold
        # Now combine and threshold
        cost_matrix = self._lambda * pos_cost + (1 - self._lambda) * app_cost
        cost_matrix[np.logical_or(pos_gate, app_gate)] = linear_assignment.INFTY_COST
        # Return Matrix
        return cost_matrix

    def _match(self, detections):
        # Split track set into confirmed and unconfirmed tracks.
        confirmed_tracks = [i for i, t in enumerate(self.tracks) if t.is_confirmed()]
        unconfirmed_tracks = [i for i, t in enumerate(self.tracks) if not t.is_confirmed()]

        # Associate confirmed tracks using appearance features.
        matches_a, unmatched_tracks_a, unmatched_detections = linear_assignment.matching_cascade(
            self._full_cost_metric,
            linear_assignment.INFTY_COST - 1,  # no need for self.metric.matching_threshold here,
            self.max_age,
            self.tracks,
            detections,
            confirmed_tracks,
        )

        # Associate remaining tracks together with unconfirmed tracks using IOU.
        iou_track_candidates = unconfirmed_tracks + [
            k for k in unmatched_tracks_a if self.tracks[k].time_since_update == 1
        ]
        unmatched_tracks_a = [
            k for k in unmatched_tracks_a if self.tracks[k].time_since_update != 1
        ]
        matches_b, unmatched_tracks_b, unmatched_detections = linear_assignment.min_cost_matching(
            iou_matching.iou_cost,
            self.max_iou_distance,
            self.tracks,
            detections,
            iou_track_candidates,
            unmatched_detections,
        )

        matches = matches_a + matches_b
        unmatched_tracks = list(set(unmatched_tracks_a + unmatched_tracks_b))
        return matches, unmatched_tracks, unmatched_detections

    def _initiate_track(self, detection, class_id):
        mean, covariance = self.kf.initiate(detection.to_xyah())
        self.tracks.append(Track(
            mean, covariance, self._next_id, class_id, self.n_init, self.max_age,
            detection.feature))
        self._next_id += 1
