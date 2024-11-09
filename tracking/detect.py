import numpy as np
import subprocess as sp
import supervision as sv

from tqdm import tqdm
from ultralytics import YOLO

from utils.team import TeamClassifier
from utils.homography import inf_main


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
    ball_detections = detections[detections.class_id == BALL_ID]
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
        [ball_detections, players_detections,
            goalkeeper_detections, referees_detections]
    )

    return updated


def get_coords(frame, detections, project=False):
    coords = detections.xyxy

    if project:
        coords = inf_main(frame, coords)

    tracking_ids = detections.tracker_id
    class_ids = detections.class_id

    return list(zip(tracking_ids, class_ids, coords))


def detections(clip_path, finetune_path, confidence=0.3, project=False, return_class=False, verbose=False):
    model = YOLO(finetune_path)

    tracker = sv.ByteTrack()
    tracker.reset()

    video_info = sv.VideoInfo.from_video_path(clip_path)
    team_classifier = classifier(
        model, clip_path, video_info, confidence=confidence)

    frame_generator = sv.get_video_frames_generator(clip_path)

    detect = []
    for frame in tqdm(frame_generator, total=video_info.total_frames) if verbose else frame_generator:
        result = model(frame, conf=confidence, verbose=False)[0]

        detections = sv.Detections.from_ultralytics(result)
        detections = detections.with_nms(
            threshold=0.5,
            class_agnostic=True,
        )
        detections = tracker.update_with_detections(detections)
        detections = team_detection(frame, detections, team_classifier)
        detections.class_id = detections.class_id.astype(int)

        if return_class:
            detect.append(detections)
        else:
            detect.append(get_coords(frame, detections, project=project))

    return detect
