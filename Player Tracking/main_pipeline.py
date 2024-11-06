import argparse
from utilities import annotate_video

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, help='input data path')
    parser.add_argument('--output', type=str, help='output data path')
    args = parser.parse_args()

    annotate_video(args.input, args.output)