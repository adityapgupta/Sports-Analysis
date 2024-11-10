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
import server_functions as srvr
cvideo = "snmot-60.mp4"

video_prefix = srvr.vid_rel_prefix
data_prefix = srvr.data_rel_prefix
df = srvr.getTrackingData(cvideo)
df_identity = srvr.getObjectsInfo(cvideo)

async def handler(webs):
    global cvideo, df, video_prefix, data_prefix, df_identity
    while True:
        message = await webs.recv()
        print(message)
        try:
            jsval:dict = json.loads(message)
            match jsval['type']:
                case 'getFiles':
                    videos = srvr.getVideoList()
                    await webs.send(json.dumps({
                                'type': 'vidList',
                                'data': videos,
                                'prefix': video_prefix
                            }))
                case 'bufVid':
                    mval, maxval = jsval['min'], jsval['max']
                    # if jsval['video'] != cvideo:
                    cvideo = jsval['video']
                    df = srvr.getTrackingData(cvideo)
                    df_identity = srvr.getObjectsInfo(cvideo)
                    frames = df.loc[df['frame'].between(mval, maxval)]
                    frame_dict = {}
                    for frame, group in frames.groupby('frame'):
                        frame_dict[frame] = group[['user', 'x', 'y', 'w', 'h']].to_dict(orient='records')
                    print("frames", frames)
                    print("df", df.head())
                    await webs.send(json.dumps({
                        'type': 'bufferedFrames',
                        'data': frame_dict
                    }))
                    await webs.send(json.dumps({
                        'type': 'player_info',
                        'data': df_identity.values.tolist()
                    }))
                case 'updatePlayers':
                    with open(f"{data_prefix}{cvideo}/player_identity.txt" , 'w') as f:
                        c = csv.writer(f)
                        c.writerows(jsval['data'])
                case 'loadFile':
                    shutil.copy(f"{jsval['file']}", f"{video_prefix}{Path(jsval['file']).name}")
                    srvr.handleTraining(Path(jsval['file']).name)
                    webs.send(json.dumps({
                        'type': 'fileSaveEvent',
                        "success": True
                    }))
                case 'getHeatmapData':
                    await webs.send(json.dumps({
                        'type': 'heatmapData',
                        'data': {
                            'left-team': srvr.getHeatmapData("as"),
                            'right-team': srvr.getHeatmapData("as"),
                            'ball': srvr.getHeatmapData("as")
                            }
                    }))
                case 'getLinemapData':
                    await webs.send(json.dumps({
                        'type': 'linemapData',
                        'data': {
                            'left-team': srvr.getLinemapData("as"),
                            'right-team': srvr.getLinemapData("as"),
                            'ball': srvr.getLinemapData("as")
                            }
                    }))
                case 'getPosessionData':
                    await webs.send(json.dumps({
                        'type': 'posessionData',
                        'data': list(srvr.getPosessionData("as"))
                    }))
                case 'getPlayerMap':
                    await webs.send(json.dumps({
                        'type': 'playerMap',
                        'data': srvr.getPlayerMap("as")
                    }))
                case 'get2dMap':
                    await webs.send(json.dumps({
                        'type': '2dMap',
                        'data': srvr.get2dData("as")
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