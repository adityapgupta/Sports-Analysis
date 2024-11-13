import pickle
import numpy as np
import pandas as pd


def interpolate(frames, k, mode):
    x, y = 0, 0
    weights = [2/14, 3/14, 4/14, 3/14, 2/14]

    for i, frame in enumerate(frames):
        if mode == 'players':
            x += frame[k][2][0] * weights[i]
            y += frame[k][2][1] * weights[i]
        elif mode == 'edges':
            x += frame[k][0] * weights[i]
            y += frame[k][1] * weights[i]

    return x, y


def ball_interpolate(pkl_path):
    with open(pkl_path, 'rb') as f:
        _, data_list = pickle.load(f)

    ball_data = pd.DataFrame(columns=['frame', 'x', 'y'])

    for i, (f, _) in enumerate(data_list):
        for track, _, (x, y) in f:
            if track == -1 and x > 0 and y > 0 and x < 105 and y < 68:
                ball_data.loc[i] = {'frame': i, 'x': x, 'y': y}
            else:
                ball_data.loc[i] = {'frame': i, 'x': np.nan, 'y': np.nan}
            break

    ball_data = ball_data.interpolate()
    ball_data = list(zip(ball_data['x'], ball_data['y']))

    return ball_data


def players_interpolate(pkl_path):
    with open(pkl_path, 'rb') as f:
        _, data_list = pickle.load(f)

    players_data = []

    for i in range(2, len(data_list) - 2):
        frames = [data_list[i + j][0] for j in range(-2, 3)]
        common_pts = set.intersection(
            *(set(f[0] for f in frame) for frame in frames))

        frames = [[f for f in frame if f[0] in common_pts] for frame in frames]
        frames = [sorted(frame, key=lambda x: x[0]) for frame in frames]

        interpolated_pts = [interpolate(frames, k, 'players') for k in range(
            len(frames[2])) if frames[2][k][0] != -1]

        tracking_ids = [frames[2][k][0]
                        for k in range(len(frames[2])) if frames[2][k][0] != -1]
        class_ids = [frames[2][k][1]
                     for k in range(len(frames[2])) if frames[2][k][0] != -1]

        players_data.append(
            list(zip(tracking_ids, class_ids, interpolated_pts)))

    return players_data


def edges_interpolate(pkl_path):
    with open(pkl_path, 'rb') as f:
        _, data_list = pickle.load(f)

    edges_data = []

    for i in range(2, len(data_list) - 2):
        edges = []
        for j in range(-2, 3):
            if len(data_list[i + j][1]) == 0:
                for k in range(i+j-1, -1, -1):
                    if len(data_list[k][1]) > 0:
                        edges.append(data_list[k][1])
                        break
            else:
                edges.append(data_list[i + j][1])

        vertices = [interpolate(edges, k, 'edges')
                    for k in range(len(edges[2]))]

        edges_data.append(vertices)

    return edges_data
