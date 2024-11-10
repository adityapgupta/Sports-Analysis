import cv2
import numpy as np
import supervision as sv


color_map = {
    0: (255, 255, 255),
    1: (255, 0, 0),
    2: (0, 0, 255),
    3: (0, 255, 0),
}


def annotators():
    ellipse_annotator = sv.EllipseAnnotator(
        color=sv.ColorPalette.from_hex(['#FFD700', '#FF1493', '#00BFFF']),
        thickness=2
    )
    label_annotator = sv.LabelAnnotator(
        color=sv.ColorPalette.from_hex(['#FFD700', '#FF1493', '#00BFFF']),
        text_color=sv.Color.from_hex('#000000'),
        text_position=sv.Position.BOTTOM_CENTER,
    )
    triangle_annotator = sv.TriangleAnnotator(
        color=sv.Color.from_hex('#FFD700'),
        base=20, height=17
    )

    return ellipse_annotator, label_annotator, triangle_annotator


def draw_markers(clip_path, out_path, detections, ball_id=0):
    video_info = sv.VideoInfo.from_video_path(clip_path)
    video_sink = sv.VideoSink(out_path, video_info)

    ellipse_annotator, label_annotator, triangle_annotator = annotators()

    frame_generator = sv.get_video_frames_generator(clip_path)
    detections_copy = detections.copy()

    with video_sink:
        for frame in frame_generator:
            frame_detections = detections_copy.pop(0)

            ball_detections = frame_detections[frame_detections.class_id == ball_id]
            ball_detections.xyxy = sv.pad_boxes(
                xyxy=ball_detections.xyxy,
                px=10,
            )
            frame_detections = frame_detections[frame_detections.class_id != ball_id]

            labels = [
                f'{int(tracker_id)}' for tracker_id in frame_detections.tracker_id]

            annotated_frame = frame.copy()
            annotated_frame = ellipse_annotator.annotate(
                annotated_frame, frame_detections)
            annotated_frame = label_annotator.annotate(
                annotated_frame, frame_detections, labels)
            annotated_frame = triangle_annotator.annotate(
                annotated_frame, ball_detections)

            video_sink.write_frame(annotated_frame)


def draw_minimap(ball_data, players_data, edges_data, out_path, image_path='tracking/utils/field.png', dimensions=(640, 480), fps=25):
    writer = cv2.VideoWriter(
        out_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, dimensions)
    field = cv2.imread(image_path)

    for i in range(len(players_data)):
        frame = field.copy()
        mask = np.zeros_like(frame)

        vertices = np.array(edges_data[i]).reshape((-1, 1, 2))
        vertices[:, :, 0] = vertices[:, :, 0] * dimensions[0]
        vertices[:, :, 1] = vertices[:, :, 1] * dimensions[1]
        vertices = vertices.astype(np.int32)

        cv2.fillPoly(mask, [vertices], (255, 255, 255))
        mask = cv2.addWeighted(frame, 0.5, mask, 1, 0)

        for _, class_id, (x, y) in players_data[i]:
            x = int(x * dimensions[0])
            y = int(y * dimensions[1])

            color = color_map[class_id]
            cv2.circle(frame, (x, y), 6, color, -1)

        if len(ball_data) > i + 2:
            x, y = ball_data[i + 2]
            x = int(x * dimensions[0])
            y = int(y * dimensions[1])

            color = color_map[0]
            cv2.circle(frame, (x, y), 4, color, -1)
            cv2.circle(frame, (x, y), 4, (0, 0, 0), 2)

        frame = cv2.bitwise_and(frame, mask)
        writer.write(frame)

    writer.release()
