import os
import argparse

import tracking.interpolate as interpolate
from tracking.detect import detections
from tracking.draw import draw_markers, draw_minimap
from analytics.visualization import visualize

cdir = os.path.dirname(os.path.abspath(__file__))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sports Analysis')
    
    parser.add_argument(
        '--clip_path',
        type=str, 
        default=f'{cdir}/results/trimmed/trimmed.mp4', 
        help='Path to the video clip',
    )
    parser.add_argument(
        '--players_path', 
        type=str, 
        default=f'{cdir}/models/players.pt', 
        help='Path to the players model'
    )
    parser.add_argument(
        '--ball_path', 
        type=str, 
        default=f'{cdir}/models/ball.pt', 
        help='Path to the ball model',
    )
    parser.add_argument(
        '--detections_path', 
        type=str, 
        default=f'{cdir}/results/trimmed/detections_trimmed.pkl', 
        help='Path to the detections pkl file',
    )
    parser.add_argument(
        '--analyze_path',
        type=str,
        default=None,
        help='Path to the analysis pkl file'
    )
    parser.add_argument(
        '--markers_path', 
        type=str, 
        default=f'{cdir}/results/trimmed/markers_trimmed.mp4', 
        help='Path to the output markers video'
    )
    parser.add_argument(
        '--minimap_path', 
        type=str, 
        default=f'{cdir}/results/trimmed/minimap_trimmed.mp4', 
        help='Path to the output minimap video'
    )
    parser.add_argument(
        '--players_conf', 
        type=float, 
        default=0.3, 
        help='Confidence level for players'
    )
    parser.add_argument(
        '--ball_conf', 
        type=float, 
        default=0.5, 
        help='Confidence level for ball'
    )
    parser.add_argument(
        '--project', 
        type=bool, 
        default=True, 
        help='Project the detections to the 2D plane'
    )
    parser.add_argument(
        '--dimensions', 
        type=tuple, 
        default=(640, 480), 
        help='Dimensions of the minimap'
    )
    parser.add_argument(
        '--fps', 
        type=int, 
        default=25, 
        help='Frames per second of the video'
    )
    parser.add_argument(
        '--statistic', 
        type=str, 
        default='voronoi', 
        help='Metric to visualize'
    )
    parser.add_argument(
        '--player_id', 
        type=int, 
        default=1, 
        help='Player ID for the metric'
    )
    parser.add_argument(
        '--frame_id', 
        type=int, 
        default=0, 
        help='Frame number for the metric'
    )
    parser.add_argument(
        '--times', 
        type=list, 
        default=None, 
        help='Times for the metric'
    )
    parser.add_argument(
        '--show', 
        type=bool, 
        default=True, 
        help='Show the visualization'
    )
    parser.add_argument(
        '--verbose', 
        type=bool, 
        default=True, 
        help='Show the progress of the detections'
    )

    args = parser.parse_args()

    # paths for the video, models and output files
    # change the clip_path to the path of the video you want to analyze
    clip_path = args.clip_path

    # path to the models
    # do not change if using the provided models
    players_path = args.players_path
    ball_path = args.ball_path

    # path to the output files
    # change according to your needs
    detections_path = args.detections_path
    analyze_path = args.analyze_path
    markers_path = args.markers_path
    minimap_path = args.minimap_path

    # run the detections on the video
    # set individual confidence levels for players and ball using players_conf and ball_conf
    # set project to False if you do not want to project the detections to the 2D plane
    detections(
        clip_path, 
        players_path, 
        ball_path, 
        detections_path, 
        players_conf=args.players_conf,
        ball_conf=args.ball_conf,
        project=args.project,
        verbose=args.verbose,
    )

    # draw the detections on the video
    draw_markers(clip_path, markers_path, detections_path)

    # interpolate and smoothen the data for analysis
    ball_data = interpolate.ball_interpolate(detections_path)
    players_data = interpolate.players_interpolate(detections_path)
    edges_data = interpolate.edges_interpolate(detections_path)

    # draw the minimap
    # set the dimensions of the minimap using dimensions
    # set the frames per second of the video using fps
    draw_minimap(
        ball_data, 
        players_data, 
        edges_data, 
        minimap_path,
        dimensions=args.dimensions,
        fps=args.fps,
    )

    # visualize the data for a metric
    # can choose voronoi, heatmap, ball, speed
    # choose the other required parameters accordingly by referring to the README file in the analytics folder
    visualize(
        detections_path, 
        statistic=args.statistic, 
        player_id=args.player_id,
        frame_id=args.frame_id,
        times=args.times,
        show=args.show,
        save_path=analyze_path,
    )
