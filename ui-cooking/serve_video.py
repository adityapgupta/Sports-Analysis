import cv2
import subprocess as sp
import asyncio
from websockets.asyncio.server import serve
import numpy
import os
import pandas as pd
import json
from http.server import SimpleHTTPRequestHandler, HTTPServer
import threading

cvideo = "snmot-60.mp4"
df:pd.DataFrame = pd.read_csv(f"./media-videos/outputs/{cvideo}.txt", header=0, names=['frame', 'user', 'x', 'y', 'w', 'h'], index_col=False)
# go into frontend/ in a cli and run `python -m http.server`
# remember to run this file first


async def handler(webs):
    global cvideo, df
    while True:
        message = await webs.recv()
        print(message)
        try:
            jsval:dict = json.loads(message)
            match jsval['type']:
                case 'getFiles':
                    videos = os.listdir('./frontend/media-videos/')
                    await webs.send(json.dumps({
                                'type': 'vidList',
                                'data': videos
                            }))
                case 'bufVid':
                    mval, maxval = jsval['min'], jsval['max']
                    if jsval['video'] != cvideo:
                        cvideo = jsval['video']
                        df = pd.read_csv(f"./media-videos/outputs/{cvideo}.txt", header=0, names=['frame', 'user', 'x', 'y', 'w', 'h'], index_col=False)
                    print(df.head())
                    frames = df.loc[df['frame'].between(mval, maxval)]
                    frame_dict = {}
                    for frame, group in frames.groupby('frame'):
                        frame_dict[frame] = group[['user', 'x', 'y', 'w', 'h']].to_dict(orient='records')
                    await webs.send(json.dumps({
                        'type': 'bufferedFrames',
                        'data': frame_dict
                    }))
        except Exception as e:
            pass

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='./frontend/media-videos', **kwargs)

def start_http_server():
    handler = CustomHTTPRequestHandler
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