import supervision as sv
from tqdm import tqdm


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


def draw(clip_path, out_path, detections, ball_id=0, verbose=False):
    video_info = sv.VideoInfo.from_video_path(clip_path)
    video_sink = sv.VideoSink(out_path, video_info)

    ellipse_annotator, label_annotator, triangle_annotator = annotators()

    frame_generator = sv.get_video_frames_generator(clip_path)

    with video_sink:
        for frame in tqdm(frame_generator, total=video_info.total_frames) if verbose else frame_generator:
            frame_detections = detections.pop(0)

            ball_detections = frame_detections[frame_detections.class_id == ball_id]
            ball_detections.xyxy = sv.pad_boxes(
                xyxy=ball_detections.xyxy,
                px=10,
            )
            frame_detections = frame_detections[frame_detections.class_id != ball_id]

            labels = [
                f'{tracker_id}' for tracker_id in frame_detections.tracker_id]

            annotated_frame = frame.copy()
            annotated_frame = ellipse_annotator.annotate(
                annotated_frame, frame_detections)
            annotated_frame = label_annotator.annotate(
                annotated_frame, frame_detections, labels)
            annotated_frame = triangle_annotator.annotate(
                annotated_frame, ball_detections)

            video_sink.write_frame(annotated_frame)
