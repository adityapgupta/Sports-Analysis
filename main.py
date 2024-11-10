import pickle
import tracking.minimap as minimap
from tracking.detect import detections
from tracking.draw import draw_markers, draw_minimap

clip_path = 'results/trimmed/trimmed.mp4'
players_path = 'models/players.pt'
ball_path = 'models/ball.pt'

pkl_path = 'results/trimmed/trimmed.pkl'
markers_path = 'results/trimmed/markers_trimmed.mp4'
minimap_path = 'results/trimmed/minimap_trimmed.mp4'

x, y = detections(clip_path, players_path, ball_path,
                  return_class=True, verbose=True)

with open(pkl_path, 'wb') as f:
    pickle.dump((x, y), f)

draw_markers(clip_path, markers_path, x)

ball_data = minimap.ball_interpolate(y)
players_data = minimap.players_interpolate(y)
edges_data = minimap.edges_interpolate(y)

draw_minimap(ball_data, players_data, edges_data, minimap_path)
