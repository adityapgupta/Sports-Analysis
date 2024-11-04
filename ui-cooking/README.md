## Install
### Python dependencies
Install websockets `pip install websockets`
### Javascript dependencies
Go into testui/ and run `npm install`

## Running
Run the python file [serve_video.py](./serve_video.py) first.

Now do `npm run dev` for development, or `npm run build & npm run preview` to generate final files

## More details

The python file communicates via localhost port 8000 (for media) and 8001 (for data). Ensure these are free