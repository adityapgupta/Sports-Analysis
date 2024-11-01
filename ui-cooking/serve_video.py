import cv2
import subprocess as sp
import asyncio
from websockets.asyncio.server import serve
import numpy
import pandas as pd
import json

df:pd.DataFrame = pd.read_csv("./media-videos/SNMOT-060/det/det.txt", header=0, names=['frame', 'user', 'x', 'y', 'w', 'h'], index_col=False)
# go into frontend/ in a cli and run `python -m http.server`
# remember to run this file first


async def handler(webs):
    while True:
        message = await webs.recv()
        print(message)
        try:
            jsval:dict = json.loads(message)
            if jsval['data'] == 'boxes':
                await webs.send(df.loc[df['frame'] == 1, ['x', 'y', 'w', 'h']].to_json(orient='records'))

        except Exception as e:
            print(e)

async def send_data(webs, num, txt):
    message = {"num": num, "text": txt}
    await webs.send(json.dumps(message))

async def main_loop():
    async with serve(handler, "", 8001):
        await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    asyncio.run(main_loop())