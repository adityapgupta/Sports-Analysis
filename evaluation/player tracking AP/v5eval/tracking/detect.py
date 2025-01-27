import os
import sys
import pickle
import warnings
import numpy as np
import subprocess as sp
import supervision as sv

from tqdm import tqdm
from ultralytics import YOLO

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils2.team import TeamClassifier
from utils2.homography import inf_main

warnings.filterwarnings('ignore')

BALL_ID = 0
PLAYER_ID = 1
GOALKEEPER_ID = 2
REFEREE_ID = 3
DEVICE = 'cuda'


def make_video(clip_path, out_path):
    """
    Makes a video from the images in the clip_path folder.

    Requires ffmpeg to be installed.
    """
    ffmpeg_path = 'ffmpeg'
    command = [
        ffmpeg_path,
        '-i', f'{clip_path}/%06d.jpg',
        '-r', '25', # fps
        '-y',
        '-v', 'quiet',
        '-c:v', 'libx264',
        f'{out_path}'
    ]
    sp.run(command)


def extract_crops(model, source_video_path, stride, player_id, confidence=0.3):
    """
    Returns the crops of the frame where the player is detected in the video.

    Uses the bounding box of the detection to crop the image.
    """
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
    """
    Separates the players in the video into two teams using the SigLIP model
    """
    stride = video_info.fps

    crops = extract_crops(
        model,
        clip_path,
        stride,
        PLAYER_ID,
        confidence=confidence
    )

    # Initialize the TeamClassifier model and fit it to the crops
    # team_classifier = TeamClassifier(device=DEVICE, verbose=False)
    # team_classifier.fit(crops)

    # return team_classifier


def goalkeepers_team(players, goalkeepers):
    """
    Decides the team of the goalkeeper based on the distance
    between the goalkeeper and the centroid of the players of each team
    """
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
    """
    Assigns a team to the detected players
    """
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
    """
    Returns the tracking ids, class ids and coordinates of the detections.

    If project is True, the coordinates are projected to the 2D plane.
    """
    coords = detections.xyxy
    tracking_ids = detections.tracker_id
    class_ids = detections.class_id

    if project:
        coords, edges = inf_main(frame, coords)
        return (list(zip(tracking_ids, class_ids, coords)), edges)

    return list(zip(tracking_ids, class_ids, coords))


def detections(clip_path, players_path, ball_path, pkl_path, players_conf=0.3, ball_conf=0.5, project=True, verbose=False):
    """
    Detects the players and the ball in the video and saves the detections in a pickle file.

    Detection confidence for players and ball can be set using players_conf and ball_conf respectively.
    If return_class is True, the detection class is saved. This is used to make the video.
    If project is True, the detections are projected to the 2D plane. This is used to make the minimap.
    """
    players_model = YOLO(players_path)
    ball_model = YOLO(ball_path)

    # tracking ids are maintained using ByteTrack
    tracker = sv.ByteTrack()
    tracker.reset()

    video_info = sv.VideoInfo.from_video_path(clip_path)
    # initialize the team classifier model using a frame from every second of the video
    # team_classifier = classifier(
    #     players_model, clip_path, video_info, confidence=players_conf)

    frame_generator = sv.get_video_frames_generator(clip_path)

    detect = []
    coordinates = []

    for frame in tqdm(frame_generator, total=video_info.total_frames) if verbose else frame_generator:
        # detect players in the frame
        player_result = players_model(
            frame, conf=players_conf, verbose=False)[0]

        players_detections = sv.Detections.from_ultralytics(player_result)
        players_detections = players_detections.with_nms(
            threshold=0.5,
            class_agnostic=True,
        )

        # update the tracker with the new detections
        players_detections = tracker.update_with_detections(players_detections)
        # players_detections = team_detection(
        #     frame, players_detections, team_classifier)
        players_detections.class_id = players_detections.class_id.astype(int)

        # detect the ball in the frame
        ball_result = ball_model(frame, conf=ball_conf, verbose=False)[0]
        ball_detections = sv.Detections.from_ultralytics(ball_result)

        # accounting for frames where no players or balls are detected
        if len(players_detections) == 0:
            players_detections.tracker_id = np.array([])

        if len(ball_detections) == 0:
            ball_detections.tracker_id = np.array([])
        else:
            # if multiple balls are detected, choose the one with the highest confidence
            max_conf = ball_detections.confidence.max()
            ball_detections = ball_detections[ball_detections.confidence == max_conf]
            ball_detections.tracker_id = np.array([-1]*len(ball_detections))

        try:
            # merge the detections of the players and the ball
            detections = sv.Detections.merge(
                [ball_detections, players_detections])
        except:
            detections = sv.Detections.empty()
            detections.tracker_id = np.array([])

        detect.append(detections)
        # coordinates.append(get_coords(frame, detections, project=project))
    # save the detections in a pickle file
    with open(pkl_path, 'wb') as f:
        pickle.dump((detect, coordinates), f)
