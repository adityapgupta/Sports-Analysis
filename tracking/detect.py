import numpy as np
import subprocess as sp
import supervision as sv

from tqdm import tqdm
from ultralytics import YOLO

from tracking.utils.homography import inf_main
from tracking.utils.team import TeamClassifier

import warnings
warnings.filterwarnings('ignore')

BALL_ID = 0
PLAYER_ID = 1
GOALKEEPER_ID = 2
REFEREE_ID = 3
DEVICE = 'cuda'


def make_video(clip_path, out_path):
    ffmpeg_path = 'ffmpeg'
    command = [
        ffmpeg_path,
        '-i', f'{clip_path}/%06d.jpg',
        '-r', '25',
        '-y',
        '-v', 'quiet',
        '-c:v', 'libx264',
        f'{out_path}'
    ]
    sp.run(command)


def extract_crops(model, source_video_path, stride, player_id, confidence=0.3):
    frame_generator = sv.get_video_frames_generator(
        source_video_path, stride=stride
    )

    crops = []
    for frame in frame_generator:
        result = model(frame, conf=confidence, verbose=False)[0]

        detections = sv.Detections.from_ultralytics(result)
        detections = detections.with_nms(threshold=0.5, class_agnostic=True)
        detections = detections[detections.class_id == player_id]

        crops += [sv.crop_image(frame, xyxy) for xyxy in detections.xyxy]

    return crops


def classifier(model, clip_path, video_info, confidence=0.3):
    stride = video_info.fps

    crops = extract_crops(
        model,
        clip_path,
        stride,
        PLAYER_ID,
        confidence=confidence
    )

    team_classifier = TeamClassifier(device=DEVICE, verbose=False)
    team_classifier.fit(crops)

    return team_classifier


def goalkeepers_team(players, goalkeepers):
    goalkeepers_xy = goalkeepers.get_anchors_coordinates(
        sv.Position.BOTTOM_CENTER
    )
    players_xy = players.get_anchors_coordinates(sv.Position.BOTTOM_CENTER)

    team_0_centroid = players_xy[players.class_id == 0].mean(axis=0)
    team_1_centroid = players_xy[players.class_id == 1].mean(axis=0)

    goalkeepers_team_id = []
    for goalkeeper_xy in goalkeepers_xy:
        dist_0 = np.linalg.norm(goalkeeper_xy - team_0_centroid)
        dist_1 = np.linalg.norm(goalkeeper_xy - team_1_centroid)
        goalkeepers_team_id.append(0 if dist_0 < dist_1 else 1)

    return np.array(goalkeepers_team_id)


def team_detection(frame, detections, team_classifier):
    goalkeeper_detections = detections[detections.class_id == GOALKEEPER_ID]
    players_detections = detections[detections.class_id == PLAYER_ID]
    referees_detections = detections[detections.class_id == REFEREE_ID]

    players_crops = [sv.crop_image(frame, xyxy)
                     for xyxy in players_detections.xyxy]
    players_detections.class_id = team_classifier.predict(
        players_crops
    )
    goalkeeper_detections.class_id = goalkeepers_team(
        players_detections,
        goalkeeper_detections,
    )

    players_detections.class_id += 1
    goalkeeper_detections.class_id += 1

    updated = sv.Detections.merge(
        [players_detections, goalkeeper_detections, referees_detections]
    )

    return updated


def get_coords(frame, detections, project=False):
    coords = detections.xyxy
    tracking_ids = detections.tracker_id
    class_ids = detections.class_id

    if project:
        coords, edges = inf_main(frame, coords)
        return (list(zip(tracking_ids, class_ids, coords)), edges)

    return list(zip(tracking_ids, class_ids, coords))


def detections(clip_path, players_path, ball_path, players_conf=0.3, ball_conf=0.5, return_class=False, project=True, verbose=False):
    players_model = YOLO(players_path)
    ball_model = YOLO(ball_path)

    tracker = sv.ByteTrack()
    tracker.reset()

    video_info = sv.VideoInfo.from_video_path(clip_path)
    team_classifier = classifier(
        players_model, clip_path, video_info, confidence=players_conf)

    frame_generator = sv.get_video_frames_generator(clip_path)

    detect = []
    coordinates = []

    for frame in tqdm(frame_generator, total=video_info.total_frames) if verbose else frame_generator:
        player_result = players_model(
            frame, conf=players_conf, verbose=False)[0]

        players_detections = sv.Detections.from_ultralytics(player_result)
        players_detections = players_detections.with_nms(
            threshold=0.5,
            class_agnostic=True,
        )
        players_detections = tracker.update_with_detections(players_detections)
        players_detections = team_detection(
            frame, players_detections, team_classifier)
        players_detections.class_id = players_detections.class_id.astype(int)

        ball_result = ball_model(frame, conf=ball_conf, verbose=False)[0]
        ball_detections = sv.Detections.from_ultralytics(ball_result)

        if len(players_detections) == 0:
            players_detections.tracker_id = np.array([])

        if len(ball_detections) == 0:
            ball_detections.tracker_id = np.array([])
        else:
            max_conf = ball_detections.confidence.max()
            ball_detections = ball_detections[ball_detections.confidence == max_conf]
            ball_detections.tracker_id = np.array([-1]*len(ball_detections))

        try:
            detections = sv.Detections.merge(
                [ball_detections, players_detections])
        except:
            detections = sv.Detections.empty()
            detections.tracker_id = np.array([])

        if return_class:
            detect.append(detections)

        coordinates.append(get_coords(frame, detections, project=project))

    return detect, coordinates
