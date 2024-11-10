import pandas as pd
import csv
import json
import yaml
import os
import shutil
import pathlib
from random import random

cdir = pathlib.Path(__file__).parent.absolute()
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
    # Ideally this would return a dict
    out = []
    for _ in range(30):
        out.append([])
        for _ in range(15):
            out[-1].append(random())
    return out

def getLinemapData(filename):
    # The frontend needs a list of points
    out = [(0, 0)]
    for _ in range(10):
        out.append((out[-1][0] + random(), random()))
    return out


def getVideoList():
    return os.listdir(video_prefix)
