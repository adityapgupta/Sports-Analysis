import cv2
import subprocess as sp
import asyncio
from websockets.asyncio.server import serve
import numpy
import csv
import os
import shutil
from pathlib import Path
import pandas as pd
import json
from http.server import SimpleHTTPRequestHandler, HTTPServer
import threading
from random import random

def load_video_failsafe(path, names):
    try:
        return pd.read_csv(path, names=names, index_col=False)
    except:
        return pd.DataFrame(columns=names)

def make_heatmap_data():
    out = []
    for _ in range(10):
        out.append([])
        for _ in range(15):
            out[-1].append(random())
    return out

video_prefix = "media-videos/vids/"
data_prefix = "media-videos/outputs/"
cvideo = "snmot-60.mp4"

df = load_video_failsafe(f"{data_prefix}{cvideo}/player_screen_data.txt", ['frame', 'user', 'x', 'y', 'w', 'h'])
df_identity = load_video_failsafe(f"{data_prefix}{cvideo}/player_identity.txt", ['sr_no', 'identity', 'jersey'])

async def handler(webs):
    global cvideo, df, video_prefix, data_prefix, df_identity
    while True:
        message = await webs.recv()
        print(message)
        try:
            jsval:dict = json.loads(message)
            match jsval['type']:
                case 'getFiles':
                    videos = os.listdir(f'{video_prefix}')
                    await webs.send(json.dumps({
                                'type': 'vidList',
                                'data': videos,
                                'prefix': video_prefix
                            }))
                case 'bufVid':
                    mval, maxval = jsval['min'], jsval['max']
                    if jsval['video'] != cvideo:
                        cvideo = jsval['video']
                        df = load_video_failsafe(f"{data_prefix}{cvideo}/player_screen_data.txt", ['frame', 'user', 'x', 'y', 'w', 'h'])
                        df_identity = load_video_failsafe(f"{data_prefix}{cvideo}/player_identity.txt", ['sr_no', 'identity', 'jersey'])
                    print(df.head())
                    frames = df.loc[df['frame'].between(mval, maxval)]
                    frame_dict = {}
                    for frame, group in frames.groupby('frame'):
                        frame_dict[frame] = group[['user', 'x', 'y', 'w', 'h']].to_dict(orient='records')
                    await webs.send(json.dumps({
                        'type': 'bufferedFrames',
                        'data': frame_dict
                    }))
                    await webs.send(json.dumps({
                        'type': 'player_info',
                        'data': df_identity.values.tolist()
                    }))
                case 'update-players':
                    with open(f"{data_prefix}{cvideo}/player_identity.txt" , 'w') as f:
                        c = csv.writer(f)
                        c.writerows(jsval['data'])
                case 'loadFile':
                    shutil.copy(f"{jsval['file']}", f"{video_prefix}{Path(jsval['file']).name}")
                    webs.send(json.dumps({
                        'type': 'fileSaveEvent',
                        "Success": True
                    }))
                case 'getHeatmapData':
                    await webs.send(json.dumps({
                        'type': 'heatmapData',
                        'data': {
                            'left-team': make_heatmap_data(),
                            'right-team': make_heatmap_data(),
                            'ball': make_heatmap_data()
                            }
                    }))

        except Exception as e:
            print(e)

def start_http_server():
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(('localhost', 8000), handler)
    print('serving')
    httpd.serve_forever()

async def send_data(webs, num, txt):
    message = {"num": num, "text": txt}
    await webs.send(json.dumps(message))

async def main_loop():
    async with serve(handler, "", 8001):
        await asyncio.get_running_loop().create_future()
http_thread = threading.Thread(target=start_http_server)
http_thread.start()
asyncio.run(main_loop())