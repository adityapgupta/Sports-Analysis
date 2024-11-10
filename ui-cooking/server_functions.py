import pandas as pd
import csv
import json
import yaml
import os
import shutil
import pathlib
from random import random
import sys
sys.path.append(str(pathlib.Path(__file__).parent.parent.absolute()))
import Soccer_Analytics.core.team_shape_analyzer as tsa

cdir = pathlib.Path(__file__).parent.absolute()
cvid = ""

vid_rel_prefix = "media-videos/vids/"
data_rel_prefix = "media-videos/outputs/"
data_prefix = f"{cdir}/media-videos/outputs/"
video_prefix = f"{cdir}/media-videos/vids/"
# ALL FILEPATHS DO NOT CONTAINE A LEADING /

def getTrackingData(filename):
    try:
        return pd.read_csv(f"{data_prefix}{filename}/player_screen_data.txt", names=['frame', 'user', 'x', 'y', 'w', 'h'], index_col=False)
    except:
        return pd.DataFrame(columns=['frame', 'user', 'x', 'y', 'w', 'h'])

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