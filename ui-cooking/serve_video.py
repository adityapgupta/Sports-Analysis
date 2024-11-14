import cv2
import subprocess as sp
import asyncio
from websockets.asyncio.server import serve
import numpy
import traceback
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
cvideo = ""

video_prefix = srvr.vid_rel_prefix
data_prefix = srvr.data_rel_prefix

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
                    df = srvr.readScreenSpaceData(cvideo)
                    frames = df.loc[df['frame'].between(mval, maxval)]
                    frame_dict = {}
                    for frame, group in frames.groupby('frame'):
                        frame_dict[frame] = group[['id', 'x', 'y', 'w', 'h']].to_dict(orient='records')
                    await webs.send(json.dumps({
                        'type': 'bufferedFrames',
                        'data': frame_dict
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
                        'data': srvr.getHeatmapData(cvideo)
                    }))
                case 'getPosessionData':
                    await webs.send(json.dumps({
                        'type': 'posessionData',
                        'data': {
                            'time_possession': srvr.getPosessionData(cvideo),
                            'team_possession': srvr.getOtherPosessionData(cvideo)['team_possession'],
                            'zone_possession': srvr.getOtherPosessionData(cvideo)['zone_possession']
                        }
                    }))
                case 'getPlayerMap':
                    await webs.send(json.dumps({
                        'type': 'playerMap',
                        'data': srvr.generateObjectMap(cvideo)
                    }))
                case 'get2dMap':
                    await webs.send(json.dumps({
                        'type': '2dMap',
                        'data': srvr.getMinimapData(cvideo),
                        'quad': srvr.getQuadData(cvideo)
                    }))
                # case 'calculatePass':
                #     await webs.send(json.dumps({
                #         'type': 'passData',
                #         'data': srvr.getPasses(jsval['frame'], jsval['pid'])
                #     }))
        except Exception as e:
            await webs.send(json.dumps({
                'type': 'error',
                'data': traceback.format_exc()
            }))
            e

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