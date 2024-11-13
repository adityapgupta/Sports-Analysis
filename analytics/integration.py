import os
import sys
import yaml
import pickle
import numpy as np

from copy import deepcopy
from datetime import datetime

cdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cdir)
from utils.heatmaps import HeatMapAnalyzer
from utils.ball import BallPossessionAnalyzer
from utils.control import SpaceControlAnalyzer
from utils.passing import PassingOpportunitiesAnalyzer


def frame_velocity(player_positions, frame_rate):
    player_velocity = {}
    for player in player_positions.keys():
        player_position = player_positions[player]
        player_velocity[player] = [(0, 0)]

        for i in range(1, len(player_position)):
            frame_diff = player_position[i][0] - player_position[i-1][0]
            time_diff = frame_diff/frame_rate
            position_diff = np.array(player_position[i][1]) - np.array(player_position[i-1][1])

            velocity = position_diff/time_diff
            velocity = tuple(velocity)
            player_velocity[player].append(velocity)

    return player_velocity


def ball_possession_integrate(data, times = None):
    analyzer = BallPossessionAnalyzer()

    field_length = analyzer.field_length
    field_width = analyzer.field_width
    frame_rate = analyzer.frame_rate

    ball_pos = np.array([field_length/2, field_width/2])

    if times:
        num_frames = int(times*frame_rate)
        data = data[:num_frames]

    for j, frame in enumerate(data):
        home_positions = []
        away_positions = []

        num_objects = len(frame)

        for i in range(num_objects):
            if frame[i][1] == 0:
                ball_pos = frame[i][2]
            elif frame[i][1] == 1:
                home_positions.append((frame[i][0], frame[i][2]))
            elif frame[i][1] == 2:
                away_positions.append((frame[i][0], frame[i][2]))

        timestamp = datetime.fromtimestamp(j/frame_rate)

        analyzer.analyze_possession(timestamp, ball_pos, home_positions, away_positions)
    
    stats = analyzer.get_possession_stats()
    flow_data = analyzer.data_possession_flow()

    return stats, flow_data


def space_control_integrate(data):
    analyzer = SpaceControlAnalyzer()
    remove_indices = []

    num_frames = len(data)
    for i in range(num_frames):
        num_objects = len(data[i])
        for j in range(num_objects):
            if data[i][j][1] == 0 or data[i][j][1] == 3:
                remove_indices.append([i, j])
    
    remove_indices = sorted(remove_indices, key=lambda x: x[1], reverse=True)

    for i, j in remove_indices:
        data[i].pop(j)
    
    control_history = []
    unique_players = []
    
    for i in range(num_frames):
        num_objects = len(data[i])
        for j in range(num_objects):
            if data[i][j][0] not in unique_players:
                unique_players.append(data[i][j][0])

    # Now get the position of each player with respect to time
    player_positions = {}
    for player in unique_players:
        player_positions[player] = []

    for i in range(num_frames):
        num_objects = len(data[i])
        for j in range(num_objects):
            player_id = data[i][j][0]
            player_position = data[i][j][2]
            player_positions[player_id].append(([i, player_position]))
    
    player_velocity = frame_velocity(player_positions, analyzer.frame_rate)

    for i in range(1, num_frames):
        home_positions = []
        away_positions = []

        num_objects = len(data[i])
        for j in range(num_objects):
            player = data[i][j][0]
            lists = player_positions[player]
            length = len(lists)
            for k in range(length):
                if lists[k][0] == i:
                    position = k
                    break

            velocity = player_velocity[player][position]

            if data[i][j][1] == 1:
                home_positions.append((data[i][j][0], data[i][j][2], velocity))
            elif data[i][j][1] == 2:
                away_positions.append((data[i][j][0], data[i][j][2], velocity))

        results = analyzer.analyze_space_control(home_positions, away_positions)
        control_history.append(results)

    return control_history


def passing_opportunity_integrate(data, frame_id, player_id, timestamp = 10.0):
    analyzer = PassingOpportunitiesAnalyzer()
    frame = data[frame_id]

    # Find the player position
    player_position = None
    for i in range(len(frame)):
        if frame[i][0] == player_id:
            player_position = frame[i][2]
            player_team = frame[i][1]
            break

    if player_position is None:
        print("Player not found")
        return None
    
    # Find the positions of all the other players
    other_friendly_players = []
    other_opponent_players = []

    for i in range(len(frame)):
        if frame[i][0] != player_id:
            if frame[i][1] == player_team:
                other_friendly_players.append((frame[i][0], frame[i][2]))
            else:
                other_opponent_players.append((frame[i][0], frame[i][2]))

    opportunities = analyzer.analyze_passing_opportunities(
        player_id, 
        player_position, 
        other_friendly_players, 
        other_opponent_players, 
        timestamp
    )
    best_opportunities = analyzer.get_best_opportunity()

    return opportunities, best_opportunities


def heatmap_integrate(data):
    analyzer = HeatMapAnalyzer()

    remove_indices = []
    for i in range(len(data)):
        for j in range(len(data[i])):
            if data[i][j][1] == 3:
                remove_indices.append([i, j])
    
    remove_indices = sorted(remove_indices, key=lambda x: x[1], reverse=True)

    for i, j in remove_indices:
        data[i].pop(j)

    # make a dictionary with 3 keys, left-team, right-team, ball
    player_positions = {}

    # make the lists for the keys as 15x10 dimensions zeros
    player_positions['left-team'] = np.zeros((10, 15))
    player_positions['right-team'] = np.zeros((10, 15))
    player_positions['ball'] = np.zeros((10, 15))
    last_ball_position = [analyzer.field_length/2, analyzer.field_width/2]
    ball_position = None

    # now we need to find the positions of the players and the ball
    for i in range(len(data)):
        for j in range(len(data[i])):
            if data[i][j][1] == 0:
                ball_position = data[i][j][2]
                
            x_c, y_c = analyzer.position_to_grid(data[i][j][2])

            if data[i][j][1] == 1:
                player_positions['left-team'][y_c][x_c] += 1
            elif data[i][j][1] == 2:
                player_positions['right-team'][y_c][x_c] += 1
            elif data[i][j][1] == 0:
                player_positions['ball'][y_c][x_c] += 1

        if ball_position is not None:
            last_ball_position = ball_position
            ball_position = None
        else:
            x_c, y_c = analyzer.position_to_grid(last_ball_position)
            player_positions['ball'][x_c][y_c] += 1
    
    # convert the numpy arrays to list
    player_positions['left-team'] = player_positions['left-team'].tolist()
    player_positions['right-team'] = player_positions['right-team'].tolist()
    player_positions['ball'] = player_positions['ball'].tolist()

    return player_positions


def integrate(pkl_path, out_path, config_path=f'{cdir}/config/config.yaml'):
    with open(pkl_path, 'rb') as f:
        _, data = pickle.load(f)

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    length = config['field']['length']
    width = config['field']['width']
    
    data2 = []
    for i in range(len(data)):
        data2.append(data[i][0])
    data = deepcopy(data2)

    for i in range(len(data)):
        for j in range(len(data[i])):
            data[i][j] = list(data[i][j])
            data[i][j][2] = (data[i][j][2][0]*length, data[i][j][2][1]*width)
    
    stats, flow_data = ball_possession_integrate(data)
    dataset_heat = heatmap_integrate(data)

    combined = {}
    combined['possession'] = stats
    combined['time_possession'] = flow_data
    combined['heatmap'] = dataset_heat
    
    with open(out_path, 'wb') as f:
        pickle.dump(combined, f)
