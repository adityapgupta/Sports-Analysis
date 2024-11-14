import os
import random
import shutil

from SoccerNet.Downloader import SoccerNetDownloader


def convert(box, width, height):
    """
    Converts the bounding box from (x, y, w, h) to (x_center, y_center, w, h)
    and normalizes the values between 0 and 1.
    """
    x, y, w, h = box
    x, w = x / width, w / width
    y, h = y / height, h / height

    bbox = [x + w / 2, y + h / 2, w, h]
    return bbox


def make_labels(train_path, ball=False):
    """
    Creates the labels for the images in the SoccerNet dataset
    and renames the images to include the name of the video.

    Setting 'ball' to True makes the function create labels only for the ball.
    """
    for name in os.listdir(train_path):
        for file in os.listdir(f'{train_path}/{name}/img1'):
            os.rename(
                f'{train_path}/{name}/img1/{file}',
                f'{train_path}/{name}/img1/{name}_{file}',
            )

    for name in os.listdir(train_path):
        label_path = f'{train_path}/{name}/labels'

        if os.path.exists(label_path):
            shutil.rmtree(label_path)
        os.makedirs(label_path)

        # get image width and height from metadata
        width, height = 1, 1
        with open(f'{train_path}/{name}/seqinfo.ini', 'r') as file:
            data = file.readlines()
            for line in data:
                if 'imWidth' in line:
                    width = eval(line.split('=')[1])
                elif 'imHeight' in line:
                    height = eval(line.split('=')[1])

        ball_ids = []
        goalkeeper_ids = []
        referee_ids = []

        # get the ids of the ball, goalkeeper and referee from metadata
        with open(f'{train_path}/{name}/gameinfo.ini', 'r') as file:
            data = file.readlines()
            for line in data:
                if 'ball' in line:
                    ball_ids.append(eval(line.split('=')[0].split('_')[1]))
                if 'goalkeeper' in line and not ball:
                    goalkeeper_ids.append(
                        eval(line.split('=')[0].split('_')[1]))
                if 'referee' in line and not ball:
                    referee_ids.append(eval(line.split('=')[0].split('_')[1]))

        # create labels for each image and save them in the labels folder
        with open(f'{train_path}/{name}/gt/gt.txt', 'r') as file:
            data = file.readlines()
            for line in data:
                line = [eval(i) for i in line.split(',')]
                bbox = convert(line[2:6], width, height)

                if ball:
                    class_id = 0
                else:
                    class_id = 1
                    if line[1] in ball_ids:
                        class_id = 0
                    elif line[1] in goalkeeper_ids:
                        class_id = 2
                    elif line[1] in referee_ids:
                        class_id = 3

                with open(
                    f'{train_path}/{name}/labels/{name}_{line[0]:06d}.txt', 'a'
                ) as f:
                    f.write(f'{class_id} {' '.join([str(i) for i in bbox])}\n')


def split(train_path, images_path, labels_path):
    """
    Splits the images and labels into training and validation sets.
    """
    if os.path.exists(images_path):
        shutil.rmtree(images_path)
    os.makedirs(images_path)

    os.makedirs(f'{images_path}/train')
    os.makedirs(f'{images_path}/val')

    if os.path.exists(labels_path):
        shutil.rmtree(labels_path)
    os.makedirs(labels_path)

    os.makedirs(f'{labels_path}/train')
    os.makedirs(f'{labels_path}/val')

    names = []
    for name in os.listdir(train_path):
        names.extend(os.listdir(f'{train_path}/{name}/img1'))

    names = [name.split('.')[0] for name in names]
    random.shuffle(names)
    train = names[: int(0.8 * len(names))]

    for name in os.listdir(train_path):
        img_path = f'{train_path}/{name}/img1'
        label_path = f'{train_path}/{name}/labels'

        for file in os.listdir(img_path):
            file = file.split('.')[0]

            if file in train:
                shutil.copy(
                    f'{img_path}/{file}.jpg',
                    f'{images_path}/train/',
                )
                shutil.copy(
                    f'{label_path}/{file}.txt',
                    f'{labels_path}/train/',
                )
            else:
                shutil.copy(
                    f'{img_path}/{file}.jpg',
                    f'{images_path}/val/',
                )
                shutil.copy(
                    f'{label_path}/{file}.txt',
                    f'{labels_path}/val/',
                )


# main function to create datasets from Soccernet dataset
# Get password from the SoccerNet website
if __name__ == '__main__':
    mySoccerNetDownloader = SoccerNetDownloader(LocalDirectory='../datasets/')
    mySoccerNetDownloader.password = 'your_password'

    mySoccerNetDownloader.downloadDataTask(
        task='tracking', split=['train', 'test']
    )

    # set ball=True for finetuning the model to detect only the ball
    make_labels('../datasets/train', ball=False)
    split(
        '../datasets/train',
        '../datasets/images',
        '../datasets/labels'
    )
