# imports
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi

# class imports
from heat_map_analyzer import HeatMapAnalyzer
from ball_possession_analyzer import BallPossessionAnalyzer
from distance_analyzer import DistanceAnalyzer
from voronoi import voronoi_finite_polygons_2d

# Visualization functions
def ball_possesion_visualization(data, times = None, last_n_events = 20, save_path = None, show = True):
  
    analyzer = BallPossessionAnalyzer()
    field_length = analyzer.field_length
    field_width = analyzer.field_width
    frame_rate = analyzer.frame_rate
    ball_pos = np.array([field_length/2, field_width/2])

    if type(times) == int:
        num_frames = int(times*frame_rate)
        data = data[:num_frames]

    if type(times) == list:
        start_frame = int(times[0]*frame_rate)
        end_frame = int(times[1]*frame_rate)

        data = data[start_frame:end_frame]


    for j, frame in enumerate(data):

        home_positions = []
        away_positions = []

        num_objects = len(frame)

        for i in range(num_objects):

            if frame[i][1] ==0:
                ball_pos = frame[i][2]
            elif frame[i][1] ==2:
                home_positions.append((frame[i][0], frame[i][2]))
            elif frame[i][1] ==1:
                away_positions.append((frame[i][0], frame[i][2]))

        timestamp = datetime.fromtimestamp(j/frame_rate)

        analyzer.analyze_possession(timestamp, ball_pos, home_positions, away_positions)
    
    
    stats = analyzer.get_possession_stats()
    
    analyzer.visualize_possession(save_path = save_path, show = show)
    analyzer.plot_possession_flow(last_n_events = last_n_events,save_path = save_path)

    return stats

def speed_visualization(data, player_id, times = None, save_path = None, show = True, smoothing_window = 10):
    
    analyzer = DistanceAnalyzer()
    frame_rate = analyzer.frame_rate

    start_time = times[0] if type(times) == list else 0
    start_frame = int(start_time*frame_rate)

    if type(times) == int:
        num_frames = int(times*frame_rate)
        data = data[:num_frames]

    if type(times) == list:
        start_frame = int(times[0]*frame_rate)
        end_frame = int(times[1]*frame_rate)

        data = data[start_frame:end_frame]

    # find frame id where player_id is present
    player_data = []
    for i in range(len(data)):
        for j in range(len(data[i])):
            if data[i][j][0] == player_id:
                player_data.append((datetime.fromtimestamp((i + start_frame)/ frame_rate), data[i][j][2]))
                
    
    for i in range(1, len(player_data)):
        analyzer.process_position(
            player_data[i][0],
            player_data[i][1],
            player_data[i-1][0],
            player_data[i-1][1]
        )

    stats = analyzer.get_distance_stats()
    analyzer.visualize_distance_breakdown(save_path = save_path, show = show)
    analyzer.plot_velocity_profile(save_path = save_path, show = show, smoothing_window = smoothing_window)

def voronoi_visualization(data, frame_id, save_path = None, show = True):
    
    frame = data[frame_id]
    
    home_positions = []
    away_positions = []
    all_positions = []
    team_colors = []

    for i in range(len(frame)):
        if frame[i][1] == 1:
            home_positions.append(frame[i][2])
            all_positions.append(frame[i][2])
            team_colors.append('red')
        elif frame[i][1] == 2:
            away_positions.append(frame[i][2])
            all_positions.append(frame[i][2])
            team_colors.append('blue')
            
    # use the voronoi diagram in scipy.spatial
    
    vor = Voronoi(all_positions)
    
    fig, ax = plt.subplots(figsize=(10.5, 6.8))
    plt.xlim([0, 105])
    plt.ylim([0, 68])
    
    
    
    regions, vertices = voronoi_finite_polygons_2d(vor)
    
    for i, region in enumerate(regions):
        polygon = vertices[region]
        point_index = vor.point_region[i] - 1
        color = team_colors[point_index]
        plt.fill(*zip(*polygon), alpha=0.5, facecolor=color, edgecolor=None)
    
    if save_path: 
        plt.savefig(save_path)
        
    if show:
        plt.show()
        
def heat_map_visualization(data, times = None, save_path = None, show = True):
    
    analyzer_away = HeatMapAnalyzer()
    analyzer_home = HeatMapAnalyzer()
    analyzer_ball = HeatMapAnalyzer()
    analyzer = HeatMapAnalyzer()
    frame_rate = analyzer.frame_rate
    
    if type(times) == int:
        num_frames = int(times*frame_rate)
        data = data[:num_frames]    
        
    if type(times) == list:
        start_frame = int(times[0]*frame_rate)
        end_frame = int(times[1]*frame_rate)

        data = data[start_frame:end_frame]

    start_time = times[0] if type(times) == list else 0
    start_frame = int(start_time*frame_rate)
    
    remove_indices = []
    for i in range(len(data)):
        for j in range(len(data[i])):
            if data[i][j][1] == 3:
                remove_indices.append([i, j])
                
    remove_indices = sorted(remove_indices, key=lambda x: x[1], reverse=True)
    
    for i, j in remove_indices:
        data[i].pop(j)
        
    home_positions = []
    away_positions = []
    ball_positions = []
    all_positions = []
    last_ball_position = [analyzer_ball.field_length/2, analyzer_ball.field_width/2]
    ball_position = None
    for i in range(len(data)):
        for j in range(len(data[i])):
            if data[i][j][1] == 0:
                ball_position = data[i][j][2]
                
            if data[i][j][1] == 1:
                home_positions.append(data[i][j][2])
                all_positions.append(data[i][j][2])
                
            if data[i][j][1] == 2:
                away_positions.append(data[i][j][2])
                all_positions.append(data[i][j][2])
                
        if ball_position is not None:
            last_ball_position = ball_position
            ball_position = None
        ball_positions.append(last_ball_position)
        
    analyzer_home.add_positions(home_positions)
    analyzer_away.add_positions(away_positions)
    analyzer_ball.add_positions(ball_positions)
    analyzer.add_positions(all_positions)
    
    if save_path:
        analyzer_home.visualize(title = 'Home Heat Map', save_path = f'{save_path}_home', show = show)
        analyzer_away.visualize(title = 'Away Heat Map', save_path = f'{save_path}_away', show = show)
        analyzer_ball.visualize(title = 'Ball Heat Map', save_path = f'{save_path}_ball', show = show)
        analyzer.visualize(title = 'All Heat Map', save_path = f'{save_path}_all', show = show)
        
    if show:
        analyzer_home.visualize(title = 'Home Heat Map')
        analyzer_away.visualize(title = 'Away Heat Map')
        analyzer_ball.visualize(title = 'Ball Heat Map')
        analyzer.visualize(title = 'All Heat Map')
        



if __name__ == "__main__":
    
    import pickle
    with open('Soccer_Analytics/core/detections.pkl', 'rb') as f:
        data = pickle.load(f)
    
    data2 = []
    for i in range(len(data)):
        data2.append(data[i][0])
    from copy import deepcopy
    
    data = deepcopy(data2)

    player_id = 14.0
    frame_id = 100
    

    speed_visualization(data, player_id, times = None, save_path = None, show = True)
    
    voronoi_visualization(data, frame_id)
 
    
    heat_map_visualization(data)
    
    # ball visualization
    ball_possesion_visualization(data, save_path = None, show = True)