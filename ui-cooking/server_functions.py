import pandas as pd
import numpy as np
import csv
import json
import yaml
import os
import shutil
import pathlib
from random import random
import supervision as spv
import sys
import pickle
sys.path.append(str(pathlib.Path(__file__).parent.parent.absolute()))
import Soccer_Analytics.core.team_shape_analyzer as tsa

cdir = pathlib.Path(__file__).parent.absolute()
cvid = ""

def currentFrame(frame):
    while True:
        yield frame

with open(f"{cdir}/media-videos/detections.pkl", 'rb') as det:
    x, y = pickle.load(det)
    print(x[0], y[0])

class_map = {
    0: "ball",
    1: "left_player",
    2: "right_player",
    3: "referee"
}
def generate_object_map(datas):
    # datas here is a list for every frame, containing (object, class, (x, y))
    workingmap = {}
    for frame, _ in datas:
        for item in frame:
            if item[0] not in workingmap:
                workingmap[int(item[0])] = class_map[item[1]]
    return workingmap

player_map = generate_object_map(y)
vid_rel_prefix = "media-videos/vids/"
data_rel_prefix = "media-videos/outputs/"
data_prefix = f"{cdir}/media-videos/outputs/"
video_prefix = f"{cdir}/media-videos/vids/"
# ALL FILEPATHS DO NOT CONTAINE A LEADING /

def readscreendata():
    with open(f"{cdir}/media-videos/detections.pkl", 'rb') as f:
        x, y = pickle.load(f)
    l2 = []
    for i, frame in enumerate(x):
        l = list(zip(currentFrame(i), frame.tracker_id.tolist(), *zip(*frame.xyxy.tolist())))
        l2.extend(l)
    df = pd.DataFrame(l2, columns=["frame", "user", "x", "y", "w", "h"])
    df['w'] = df['w'] - df['x']
    df['h'] = df['h'] - df['y']
    return df

def read2dscreendata():
    with open(f"{cdir}/media-videos/detections.pkl", 'rb') as f:
        x, y = f.read()
    l2 = []
    for i, frame in enumerate(x):
        l = list(zip(currentFrame(i), frame.tracker_id.tolist(), *zip(*frame.xyxy.tolist())))
        l2.extend(l)
    df = pd.DataFrame(l2, columns=["frame", "id", "x", "y", "w", "h"])
    df['w'] = df['w'] - df['x']
    df['h'] = df['h'] - df['y']
    return df

newdetections = []
for i in y:
    newdetections.append([])
    for (j, k, l) in i[0]:
        newdetections[-1].append([int(j), int(k), (float(l[0]), float(l[1]))])
y = newdetections

def getTrackingData(filename):
    return readscreendata()

def getObjectsInfo(filename):
    try:
        return pd.read_csv(f"{data_prefix}{filename}/player_identity.txt", ['sr_no', 'identity', 'jersey'])
    except:
        return pd.DataFrame(columns=['sr_no', 'identity', 'jersey'])

def getHeatmapData(filename):
    # The frontend expects a 10x15 grid
    # Ideally this would return a dict and the serve_video would be modified
    # The grid is of the form of [[r1c1, r2c1 ... ], [r1c2, r2c2 ...], ...]
    out = []
    for _ in range(10):
        out.append([])
        for _ in range(15):
            out[-1].append(random())
    return out

def getLinemapData(filename):
    # The frontend needs a list of points
    out = [(0, 0)]
    for _ in range(10):
        out.append((out[-1][0] + random(), random()*5))
    return out

def getPlayerMap(filename):
    # The frontend expects a dict of player number to player identity
    return player_map

def getVideoList():
    return os.listdir(video_prefix)

def getPosessionData(filename):
    start = random()
    end = start
    for i in range(10):
        start = end + random()
        end += 3*random()
        yield {'start': start, 'end': end, 'team': "left" if i % 2 == 0 else "right"}

def handleTraining(filename):
    if filename == cvid:
        print("Folder already existing")
        return
    if not os.path.exists(f"{data_prefix}{filename}"):
        os.mkdir(f"{data_prefix}{filename}")

def get2dData(filename):
    return y