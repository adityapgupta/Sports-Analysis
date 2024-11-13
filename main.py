import os

import tracking.interpolate as interpolate
from tracking.detect import detections
from tracking.draw import draw_markers, draw_minimap
from analytics.visualization import visualize


cdir = os.path.dirname(os.path.abspath(__file__))

clip_path = f'{cdir}/results/trimmed/trimmed.mp4'
players_path = f'{cdir}/models/players.pt'
ball_path = f'{cdir}/models/ball.pt'
pkl_path = f'{cdir}/results/trimmed/trimmed.pkl'

markers_path = f'{cdir}/results/trimmed/markers_trimmed.mp4'
minimap_path = f'{cdir}/results/trimmed/minimap_trimmed.mp4'


detections(clip_path, players_path, ball_path, pkl_path, return_class=True, verbose=True)
draw_markers(clip_path, markers_path, pkl_path)

ball_data = interpolate.ball_interpolate(pkl_path)
players_data = interpolate.players_interpolate(pkl_path)
edges_data = interpolate.edges_interpolate(pkl_path)

draw_minimap(ball_data, players_data, edges_data, minimap_path)

visualize(pkl_path, 'speed', player_id=15)
