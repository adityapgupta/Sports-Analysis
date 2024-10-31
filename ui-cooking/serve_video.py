import cv2
import subprocess as sp
import asyncio
from websockets.asyncio.server import serve
import numpy
import json

# go into frontend/ in a cli and run `python -m http.server`
# remember to run this file first

async def handler(webs):
    while True:
        message = await webs.recv()
        print(message)
        try:
            jsval:dict = json.loads(message)
            await send_data(webs, jsval['num']**2, jsval['text']*2)

        except Exception as b:
            print(b)

async def send_data(webs, num, txt):
    message = {"num": num, "text": txt}
    await webs.send(json.dumps(message))

async def main_loop():
    async with serve(handler, "", 8001):
        await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    asyncio.run(main_loop())