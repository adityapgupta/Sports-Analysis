import pickle
import tracking.minimap as minimap
from tracking.detect import detections
from tracking.draw import draw_markers, draw_minimap

clip_path = 'datasets/test/f.mp4'
players_path = 'models/players.pt'
ball_path = 'models/ball.pt'

x, y = detections(clip_path, players_path, ball_path,
                  return_class=True, verbose=True)

with open('detections.pkl', 'wb') as f:
    pickle.dump((x, y), f)

draw_markers(clip_path, 'markers.mp4', x)

ball_data = minimap.ball_interpolate(y)
players_data = minimap.players_interpolate(y)
edges_data = minimap.edges_interpolate(y)

draw_minimap(ball_data, players_data, edges_data, 'minimap.mp4')
