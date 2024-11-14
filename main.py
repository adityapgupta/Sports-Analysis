import os

import tracking.interpolate as interpolate
from tracking.detect import detections
from tracking.draw import draw_markers, draw_minimap
from analytics.visualization import visualize

cdir = os.path.dirname(os.path.abspath(__file__))


if __name__ == '__main__':
    # paths for the video, models and output files
    # change the clip_path to the path of the video you want to analyze
    clip_path = f'{cdir}/results/trimmed/trimmed.mp4'

    # path to the models
    # do not change if using the provided models
    players_path = f'{cdir}/models/players.pt'
    ball_path = f'{cdir}/models/ball.pt'

    # path to the output files
    # change according to your needs
    pkl_path = f'{cdir}/results/trimmed/trimmed.pkl'
    markers_path = f'{cdir}/results/trimmed/markers_trimmed.mp4'
    minimap_path = f'{cdir}/results/trimmed/minimap_trimmed.mp4'

    # run the detections on the video
    # set individual confidence levels for players and ball using players_conf and ball_conf
    # set project to False if you do not want to project the detections to the 2D plane
    detections(
        clip_path, 
        players_path, 
        ball_path, 
        pkl_path, 
        players_conf=0.3,
        ball_conf=0.5,
        project=True,
        verbose=True,
    )

    # draw the detections on the video
    draw_markers(clip_path, markers_path, pkl_path)

    # interpolate and smoothen the data for analysis
    ball_data = interpolate.ball_interpolate(pkl_path)
    players_data = interpolate.players_interpolate(pkl_path)
    edges_data = interpolate.edges_interpolate(pkl_path)

    # draw the minimap
    # set the dimensions of the minimap using dimensions
    # set the frames per second of the video using fps
    draw_minimap(
        ball_data, 
        players_data, 
        edges_data, 
        minimap_path,
        dimensions=(640, 480),
        fps=25,
    )

    # visualize the data for a metric
    # can choose voronoi, heatmap, ball, speed
    # choose the other required parameters accordingly by referring to the README file in the analytics folder
    visualize(
        pkl_path, 
        statistic='speed', 
        player_id=15,
        frame_id=100,
        times=None,
        show=True,
    )
