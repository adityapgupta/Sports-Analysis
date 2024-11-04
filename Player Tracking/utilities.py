import numpy as np
import subprocess as sp
import supervision as sv
import matplotlib.pyplot as plt
from tqdm import tqdm
from ultralytics import YOLO
from sports.sports.common.team import TeamClassifier
from inference import inf_main
import cv2

def make_video(clip_path):
    ffmpeg_path = 'ffmpeg'
    command = [
        ffmpeg_path,
        '-i', f'{clip_path}/messi_sample.png',
        '-r', '25',
        '-y',
        '-v', 'quiet',
        '-c:v', 'libx264',
        f'{clip_path}/out.mp4'
    ]
    sp.run(command)


def resolve_goalkeepers_team_id(players, goalkeepers):
    goalkeepers_xy = goalkeepers.get_anchors_coordinates(sv.Position.BOTTOM_CENTER)
    players_xy = players.get_anchors_coordinates(sv.Position.BOTTOM_CENTER)
    team_0_centroid = players_xy[players.class_id == 0].mean(axis=0)
    team_1_centroid = players_xy[players.class_id == 1].mean(axis=0)
    goalkeepers_team_id = []
    for goalkeeper_xy in goalkeepers_xy:
        dist_0 = np.linalg.norm(goalkeeper_xy - team_0_centroid)
        dist_1 = np.linalg.norm(goalkeeper_xy - team_1_centroid)
        goalkeepers_team_id.append(0 if dist_0 < dist_1 else 1)

    return np.array(goalkeepers_team_id)


def extract_crops(model, source_video_path, stride, player_id, confidence=0.3):
    frame_generator = sv.get_video_frames_generator(source_video_path, stride=stride)

    crops = []
    for frame in frame_generator:
        result = model(frame, conf=confidence, verbose=False)[0]
        detections = sv.Detections.from_ultralytics(result)
        detections = detections.with_nms(threshold=0.5, class_agnostic=True)
        detections = detections[detections.class_id == player_id]

        crops += [sv.crop_image(frame, xyxy) for xyxy in detections.xyxy]

    return crops


def annotate_video(input_path, output_path, finetune_path = "../final_models/best.pt", confidence=0.3):
    SOURCE_VIDEO_PATH = input_path
    TARGET_VIDEO_PATH = output_path
    BALL_ID = 0
    PLAYER_ID = 1
    GOALKEEPER_ID = 2
    REFEREE_ID = 3

    # ellipse_annotator = sv.EllipseAnnotator(
    #     color=sv.ColorPalette.from_hex(['#00BFFF', '#FF1493', '#FFD700']),
    #     thickness=2
    # )
    # label_annotator = sv.LabelAnnotator(
    #     color=sv.ColorPalette.from_hex(['#00BFFF', '#FF1493', '#FFD700']),
    #     text_color=sv.Color.from_hex('#000000'),
    #     text_position=sv.Position.BOTTOM_CENTER,
    # )
    # triangle_annotator = sv.TriangleAnnotator(
    #     color=sv.Color.from_hex('#FFD700'),
    #     base=20, height=17
    # )

    tracker = sv.ByteTrack()
    tracker.reset()

    video_info = sv.VideoInfo.from_video_path(SOURCE_VIDEO_PATH)
    # video_sink = sv.VideoSink(TARGET_VIDEO_PATH, video_info)
    video_writer = cv2.VideoWriter(TARGET_VIDEO_PATH, cv2.VideoWriter_fourcc(*'mp4v'), video_info.fps, (video_info.width, video_info.height))
    STRIDE = video_info.fps

    model = YOLO(finetune_path)
    crops = extract_crops(model, SOURCE_VIDEO_PATH, STRIDE, PLAYER_ID, confidence=confidence)
    team_classifier = TeamClassifier(device='cuda')
    team_classifier.fit(crops)

    frame_generator = sv.get_video_frames_generator(SOURCE_VIDEO_PATH)
    # track_set = set() 
    i = 0
    for frame in tqdm(frame_generator, total=video_info.total_frames):
            i += 1
            result = model(frame, conf=confidence, verbose=False)[0]
            detections = sv.Detections.from_ultralytics(result)
            # temp_cords = detections.xyxy
            # temp_labels = detections.data['class_name']
            cords = detections.xyxy
            labels = detections.data['class_name']
            arr = {'cords': cords, 'labels': labels}
            annotated_frame = inf_main(frame, arr)
            plt.imsave(f"./saves/{i}.png", annotated_frame)

            # ball_detections = detections[detections.class_id == BALL_ID]
            # # ball_detections.xyxy = sv.pad_boxes(xyxy=ball_detections.xyxy, px=10)
            
            # detections = detections.with_nms(threshold=0.5, class_agnostic=True)
            # detections = tracker.update_with_detections(detections)

            # goalkeeper_detections = all_detections[all_detections.class_id == GOALKEEPER_ID]
            # players_detections = all_detections[all_detections.class_id == PLAYER_ID]
            # referees_detections = all_detections[all_detections.class_id == REFEREE_ID]

            # players_crops = [sv.crop_image(frame, xyxy) for xyxy in players_detections.xyxy]
            # players_detections.class_id = team_classifier.predict(players_crops)
            
            # players_mean = []
            # for crop in players_crops:
            #     players_mean.append(crop.reshape(-1, crop.shape[-1]).mean(axis=0))

            # goalkeeper_detections.class_id = resolve_goalkeepers_team_id(players_detections, goalkeeper_detections)

            # referees_detections.class_id -= 1

            # all_detections = sv.Detections.merge([players_detections, goalkeeper_detections, referees_detections])

            # ids = detections.tracker_id
            # if i==1:
            #     track_set = set(ids)
            # # all_detections.class_id = all_detections.class_id.astype(int)
            # final_cords = []
            # final_labels = []
            # for i in range(len(ids)):
            #     if ids[i] in track_set:
            #         final_cords.append(temp_cords[i])
            #         final_labels.append(temp_labels[i])
            # track_set = set(ids)
            # arr = {'cords': final_cords, 'labels': final_labels}    
            # annotated_frame = inf_main(frame, arr)
            # plt.imsave(f"./saves/{i}.png", annotated_frame)
            # annotated_frame = frame.copy()
            # annotated_frame = ellipse_annotator.annotate(annotated_frame, all_detections)
            # annotated_frame = label_annotator.annotate(annotated_frame, all_detections, labels)
            # annotated_frame = triangle_annotator.annotate(annotated_frame, ball_detections)

            # video_sink.write_frame(annotated_frame)
            video_writer.write(annotated_frame)
    video_writer.release()
input_path = "help/examples/iniesta_sample.mp4"
output_path = "help/examples/iniesta_sample_out.mp4"
annotate_video(input_path, output_path)