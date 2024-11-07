import cv2
import yaml
import torch
import numpy as np
import matplotlib.pyplot as plt
import torchvision.transforms as T
import torchvision.transforms.functional as f
import warnings
warnings.filterwarnings("ignore")
from PIL import Image

from help.model.cls_hrnet import get_cls_net
from help.model.cls_hrnet_l import get_cls_net as get_cls_net_l

from help.utils.utils_calib import FramebyFrameCalib
from help.utils.utils_heatmap import get_keypoints_from_heatmap_batch_maxpool, get_keypoints_from_heatmap_batch_maxpool_l, \
    complete_keypoints, coords_to_dict

transform2 = T.Resize((540, 960))
device = torch.device("cuda:0")
color_map = {
    'player': (0, 0, 255),
    'ball': (255, 255, 0),
    'referee': (255, 0, 0),
    'goalkeeper': (0, 0, 0)
}
# lines_coords = [[[0., 54.16, 0.], [16.5, 54.16, 0.]],
#                 [[16.5, 13.84, 0.], [16.5, 54.16, 0.]],
#                 [[16.5, 13.84, 0.], [0., 13.84, 0.]],
#                 [[88.5, 54.16, 0.], [105., 54.16, 0.]],
#                 [[88.5, 13.84, 0.], [88.5, 54.16, 0.]],
#                 [[88.5, 13.84, 0.], [105., 13.84, 0.]],
#                 [[0., 37.66, -2.44], [0., 30.34, -2.44]],
#                 [[0., 37.66, 0.], [0., 37.66, -2.44]],
#                 [[0., 30.34, 0.], [0., 30.34, -2.44]],
#                 [[105., 37.66, -2.44], [105., 30.34, -2.44]],
#                 [[105., 30.34, 0.], [105., 30.34, -2.44]],
#                 [[105., 37.66, 0.], [105., 37.66, -2.44]],
#                 [[52.5, 0., 0.], [52.5, 68, 0.]],
#                 [[0., 68., 0.], [105., 68., 0.]],
#                 [[0., 0., 0.], [0., 68., 0.]],
#                 [[105., 0., 0.], [105., 68., 0.]],
#                 [[0., 0., 0.], [105., 0., 0.]],
#                 [[0., 43.16, 0.], [5.5, 43.16, 0.]],
#                 [[5.5, 43.16, 0.], [5.5, 24.84, 0.]],
#                 [[5.5, 24.84, 0.], [0., 24.84, 0.]],
#                 [[99.5, 43.16, 0.], [105., 43.16, 0.]],
#                 [[99.5, 43.16, 0.], [99.5, 24.84, 0.]],
#                 [[99.5, 24.84, 0.], [105., 24.84, 0.]]]


def projection_from_cam_params(final_params_dict):
    cam_params = final_params_dict["cam_params"]
    x_focal_length = cam_params['x_focal_length']
    y_focal_length = cam_params['y_focal_length']
    principal_point = np.array(cam_params['principal_point'])
    position_meters = np.array(cam_params['position_meters'])
    rotation = np.array(cam_params['rotation_matrix'])

    It = np.eye(4)[:-1]
    It[:, -1] = -position_meters
    Q = np.array([[x_focal_length, 0, principal_point[0]],
                  [0, y_focal_length, principal_point[1]],
                  [0, 0, 1]])
    P = Q @ (rotation @ It)

    return P


def inference(cam, frame, model, model_l, kp_threshold, line_threshold):
    frame = Image.fromarray(frame)

    frame = f.to_tensor(frame).float().unsqueeze(0)
    # _, _, h_original, w_original = frame.size()
    frame = frame if frame.size()[-1] == 960 else transform2(frame)
    frame = frame.to(device)
    b, c, h, w = frame.size()
    frame = frame.to(device)

    model.eval()
    model_l.eval()
    model.to(device)
    model_l.to(device)

    with torch.no_grad():
        heatmaps = model(frame)
        heatmaps_l = model_l(frame)

    kp_coords = get_keypoints_from_heatmap_batch_maxpool(heatmaps[:,:-1,:,:])
    line_coords = get_keypoints_from_heatmap_batch_maxpool_l(heatmaps_l[:,:-1,:,:])
    kp_dict = coords_to_dict(kp_coords, threshold=kp_threshold)
    lines_dict = coords_to_dict(line_coords, threshold=line_threshold)
    final_dict = complete_keypoints(kp_dict, lines_dict, w=w, h=h, normalize=True)

    cam.update(final_dict[0])
    final_params_dict = cam.heuristic_voting()

    return final_params_dict

def get_map_point(point, P):
    point = np.linalg.inv(P) @ np.array(point)
    point = point/point[2]
    point[0] += 105/2
    point[1] += 68/2
    return (point[0], point[1])

def project(P, coords):
    # fig, ax = plt.subplots()

    # for line in lines_coords:
    #     x1, y1, _ = line[0]
    #     x2, y2, _ = line[1]

    #     ax.plot([x1, x2], [y1, y2], 'white', lw=3)

    # ax.add_artist(plt.Circle((105/2, 68/2), 9.15, color='white', fill=False, lw=3))

    # points_l = []
    # for ang in np.linspace(219, 321, 200):
    #     ang = np.deg2rad(ang)
    #     point = [94 + 9.15*np.sin(ang), 68/2 + 9.15*np.cos(ang)]
    #     # Plot the arc
    #     points_l.append(point)
    # ax.plot([x for x, _ in points_l], [y for _, y in points_l], 'white', lw=3)
    
    # points_r = []
    # for ang in np.linspace(39, 141, 200):
    #     ang = np.deg2rad(ang)
    #     point = [11 + 9.15*np.sin(ang), 68/2 + 9.15*np.cos(ang)]
    #     # Plot the arc
    #     points_r.append(point)
    # ax.plot([x for x, _ in points_r], [y for _, y in points_r], 'white', lw=3)

    # pts = coords['cords']
    # labs = coords['labels']
    # pts = [get_map_point([(x1+x2)/2, y2,1], P) for x1,_,x2,y2 in pts]

    # for i, coord in enumerate(pts):
    #     x, y = coord
    #     color = color_map[labs[i]] if labs[i] in color_map else 'yellow'
    #     ax.scatter(x, y, c = color, marker='o')

    # ax.set_xlim(0, 105)
    # ax.set_ylim(0, 68)
    # ax.invert_yaxis()
    # ax.axis('off')
    # plt.tight_layout(pad=0)
    # fig.patch.set_facecolor('green')
    # return fig

    # Open ./field.png
    field = cv2.imread('field.png')

    # for i, coord in enumerate(pts):
    #     x, y = coord
    #     color = color_map[labs[i]] if labs[i] in color_map else 'yellow'
    #     ax.scatter(x, y, c = color, marker='o')

    pts = coords['cords']
    labs = coords['labels']
    pts = [get_map_point([(x1+x2)/2, y2,1], P) for x1,_,x2,y2 in pts]

    for i, coord in enumerate(pts):
        x, y = coord
        color = color_map[labs[i]] if labs[i] in color_map else (255, 255, 0)
        cv2.circle(field, (int(x)*640//105, int(y)*480//68), 4, color, -1)
        cv2.circle(field, (int(x)*640//105, int(y)*480//68), 4, (0, 0, 0), 1)
    return field



def process_input(input, coords, model, model_l, kp_threshold, line_threshold):

        frame_width = input.shape[1]
        frame_height = input.shape[0]
        cam = FramebyFrameCalib(iwidth=frame_width, iheight=frame_height, denormalize=True)

        final_params_dict = inference(cam, input, model, model_l, kp_threshold, line_threshold)

        if final_params_dict is not None:
            P = projection_from_cam_params(final_params_dict)
            # Delete 3rd column of P
            P_reduced = np.array(
                [[P[0][0], P[0][1], P[0][3]],
                [P[1][0], P[1][1], P[1][3]],
                [P[2][0], P[2][1], P[2][3]]]
          )
            projected_frame = project(P_reduced, coords)
        else:
            projected_frame = cv2.imread('./field.png')  

        # Make the projected frame into a cv2 image
        # projected_frame.canvas.draw()
        # width, height = projected_frame.canvas.get_width_height()
        # projected_frame = np.fromstring(projected_frame.canvas.tostring_rgb(), dtype='uint8', sep='')
        # projected_frame = projected_frame.reshape((height, width, 3))

        return projected_frame
# if __name__ == "__main__":

    # parser = argparse.ArgumentParser(description="Process video or image and plot lines on each frame.")
    # parser.add_argument("--weights_kp", type=str, help="Path to the model for keypoint inference.")
    # parser.add_argument("--weights_line", type=str, help="Path to the model for line projection.")
    # parser.add_argument("--kp_threshold", type=float, default=0.1486, help="Threshold for keypoint detection.")
    # parser.add_argument("--line_threshold", type=float, default=0.3880, help="Threshold for line detection.")
    # parser.add_argument("--device", type=str, default="cuda:0", help="CPU or CUDA device index")
    # parser.add_argument("--input_path", type=str, required=True, help="Path to the input video or image file.")
    # parser.add_argument("--input_type", type=str, choices=['video', 'image'], required=True,
    #                     help="Type of input: 'video' or 'image'.")
    # parser.add_argument("--save_path", type=str, default="", help="Path to save the processed video.")
    # parser.add_argument("--display", action="store_true", help="Enable real-time display.")
    # args = parser.parse_args()


#     input_path = args.input_path
#     input_type = args.input_type
#     model_kp = args.weights_kp
#     model_line = args.weights_line
#     save_path = args.save_path
#     device = args.device
#     display = args.display and input_type == 'video'
#     kp_threshold = args.kp_threshold
#     line_threshold = args.line_threshold

#     cfg = yaml.safe_load(open("config/hrnetv2_w48.yaml", 'r'))
#     cfg_l = yaml.safe_load(open("config/hrnetv2_w48_l.yaml", 'r'))

#     loaded_state = torch.load(args.weights_kp, map_location=device)
#     model = get_cls_net(cfg)
#     model.load_state_dict(loaded_state)
#     model.to(device)
#     model.eval()

#     loaded_state_l = torch.load(args.weights_line, map_location=device)
#     model_l = get_cls_net_l(cfg_l)
#     model_l.load_state_dict(loaded_state_l)
#     model_l.to(device)
#     model_l.eval()

#     transform2 = T.Resize((540, 960))

#     process_input(input_path, input_type, model_kp, model_line, kp_threshold, line_threshold, save_path, display)

def inf_main(input, coords, weights_kp ="help/weights/SV_FT_WC14_kp", weights_line="help/weights/SV_FT_WC14_lines", kp_threshold = 0.1486, line_threshold = 0.3880, device = 'cuda'):
    cfg = yaml.safe_load(open("help/config/hrnetv2_w48.yaml", 'r'))
    cfg_l = yaml.safe_load(open("help/config/hrnetv2_w48_l.yaml", 'r'))

    loaded_state = torch.load(weights_kp, map_location=device)
    model = get_cls_net(cfg)
    model.load_state_dict(loaded_state)
    model.to(device)
    model.eval()

    loaded_state_l = torch.load(weights_line, map_location=device)
    model_l = get_cls_net_l(cfg_l)
    model_l.load_state_dict(loaded_state_l)
    model_l.to(device)
    model_l.eval()

    out_frame = process_input(input, coords, model, model_l, kp_threshold, line_threshold)

    return out_frame

# arr = [[     432.22,      423.56,      458.49,      498.79],
#        [     514.62,      485.65,      541.39,      560.73],
#        [     450.68,      405.63,      478.15,      475.73],
#        [     461.13,      272.91,      492.62,      329.59],
#        [     376.87,      405.79,      400.15,      477.38],
#        [     490.25,      300.99,      517.73,      363.05],
#        [     318.47,      269.04,      338.86,      329.96],
#        [     164.51,      369.99,      192.06,      442.03],
#        [     838.78,      257.84,      861.77,      354.99],
#        [     762.38,      220.32,      787.03,      290.24],
#        [     1024.9,      582.93,      1051.2,      602.01],
#        [     280.13,       478.8,      308.02,      551.82],
#        [     165.68,      449.35,      196.14,       527.1]]

# out = inf_main(cv2.imread('help/examples/messi_sample.png'), arr, device='cpu')   

# plt.imsave('./output.png', out)