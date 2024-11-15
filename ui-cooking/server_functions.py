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
import subprocess as sp
import pickle
sys.path.append(str(pathlib.Path(__file__).parent.parent.absolute()))
import analytics.integration as analytics

if os.name == 'nt':
    python_exec = 'python'
else:
    python_exec = 'python3'

cdir = pathlib.Path(__file__).parent.absolute()
cvid = ""
tracking_data = ()
analytics_data = {}
tracking_data_2d = []
view_data_2d = []

def load_file_data(filename, force_reload = False):
    global tracking_data, analytics_data, tracking_data_2d, cvid, view_data_2d
    if (not force_reload and cvid == filename):
        return
    print("attempting to access", filename, cvid)
    cvid = filename
    try:
        with open(f"{cdir}/media-videos/outputs/{filename}/tracking_data.pkl", 'rb') as f:
            tracking_data = pickle.load(f)
            # tracking_data[1] is of the format [([(id, class, (x , y))], coordinates)]
            view_data_2d = []
            tracking_data_2d = []
            for frame in tracking_data[1]:
                tracking_data_2d.append([(int(t[0]), int(t[1]), (float(t[2][0]), float(t[2][1]))) for t in frame[0]])
                view_data_2d.append([(float(t[0]), float(t[1])) for t in frame[1]])

        with open(f"{cdir}/media-videos/outputs/{filename}/analytics.pkl", 'rb') as f:
            analytics_data = pickle.load(f)
    except FileNotFoundError:
        print(f"That file is not found, {cdir}/media-videos/outputs/{filename}/tracking_data.pkl")


def currentFrame(frame):
    while True:
        yield frame

class_map = {
    0: "ball",
    1: "left_player",
    2: "right_player",
    3: "referee"
}

def generateObjectMap(filename):
    load_file_data(filename)
    workingmap = {}
    for frame in tracking_data_2d:
        for item in frame:
            if item[0] not in workingmap:
                workingmap[int(item[0])] = class_map[item[1]]
    return workingmap

vid_rel_prefix = "media-videos/vids/"
data_rel_prefix = "media-videos/outputs/"
data_prefix = f"{cdir}/media-videos/outputs/"
video_prefix = f"{cdir}/media-videos/vids/"
# ALL FILEPATHS DO NOT CONTAINE A LEADING /

def readScreenSpaceData(filename):
    load_file_data(filename)
    if not tracking_data: return

    x = tracking_data[0]
    l2 = []
    for i, frame in enumerate(x):
        l = list(zip(currentFrame(i), frame.tracker_id.tolist(), *zip(*frame.xyxy.tolist())))
        l2.extend(l)
    df = pd.DataFrame(l2, columns=["frame", "id", "x", "y", "w", "h"])
    df['w'] = df['w'] - df['x']
    df['h'] = df['h'] - df['y']
    return df

def getHeatmapData(filename):
    load_file_data(filename)
    return analytics_data['heatmap']

def getVideoList():
    return os.listdir(video_prefix)

def getPosessionData(filename):
    load_file_data(filename)
    return analytics_data['time_possesion']

def getOtherPosessionData(filename):
    load_file_data(filename)
    return analytics_data['possesion']

def handleTraining(filename):
    if filename == cvid:
        print("Folder already existing")
        return
    if not os.path.exists(f"{data_prefix}{filename}"):
        os.mkdir(f"{data_prefix}{filename}")
    runModel(filename)

def getMinimapData(filename):
    load_file_data(filename)
    return tracking_data_2d

def getQuadData(filename):
    load_file_data(filename)
    return view_data_2d

# def getPasses(frame, pid):
#     print(analytics.passing_opportunity_integrate(tracking_data_2d, frame, pid))
#     return analytics.passing_opportunity_integrate(tracking_data_2d, frame, pid)

def runModel(filename):
    program = [
        python_exec,
        f"{cdir}/../main.py",
        "--clip_path",
        f"{cdir}/media-videos/vids/{filename}",
        "--analyze_path",
        f"{cdir}/media-videos/outputs/{filename}/analytics.pkl",
    ]
    sp.Popen(program)