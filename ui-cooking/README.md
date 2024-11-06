## Install
### Python dependencies
Install websockets `pip install websockets`
### Javascript dependencies
Go into testui/ and run `npm install`

## Input

The file structure is as follows:
```
| serve-video.py
| testui/
    | <frontend code>
| media-videos/
    | vids
        | <video-1>.mp4
        | <video-2>.mp4
        | ...
    | outputs
        | <video-1>.mp4/
            | player_identity.txt
            | player_screen_data.txt
        | <video-2>.mp4/
            | ...
        | ...
```
## Running
Run the python file [serve_video.py](./serve_video.py) from the root directory first.

Now go into testui/ and do `npm run dev` for development, or `npm run build & npm run preview` to generate final files

## More details

The python file communicates via localhost port 8000 (for media) and 8001 (for data). Ensure these are free