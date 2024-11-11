import yaml
import numpy as np
from PIL import Image

import torch
import torchvision.transforms as T
import torchvision.transforms.functional as f

from tracking.utils.hrnet import get_cls_net
from tracking.utils.calib import FramebyFrameCalib
from tracking.utils.hrnet_l import get_cls_net as get_cls_net_l
from tracking.utils.heatmap import get_keypoints_from_heatmap_batch_maxpool, \
    get_keypoints_from_heatmap_batch_maxpool_l, \
    complete_keypoints, coords_to_dict


DEVICE = torch.device('cuda')


def projection_from_cam_params(final_params_dict):
    cam_params = final_params_dict['cam_params']
    x_focal_length = cam_params['x_focal_length']
    y_focal_length = cam_params['y_focal_length']

    principal_point = np.array(cam_params['principal_point'])
    position_meters = np.array(cam_params['position_meters'])
    rotation = np.array(cam_params['rotation_matrix'])

    It = np.eye(4)[:-1]
    It[:, -1] = -position_meters

    Q = np.array([
        [x_focal_length, 0, principal_point[0]],
        [0, y_focal_length, principal_point[1]],
        [0, 0, 1],
    ])
    P = Q @ (rotation @ It)

    return P


def inference(cam, frame, model, model_l, kp_threshold, line_threshold, device=DEVICE):
    frame = Image.fromarray(frame)
    frame = f.to_tensor(frame).float().unsqueeze(0)
    frame = frame if frame.size()[-1] == 960 else T.Resize((540, 960))(frame)

    frame = frame.to(device)
    _, _, h, w = frame.size()

    model.eval()
    model.to(device)

    model_l.eval()
    model_l.to(device)

    with torch.no_grad():
        heatmaps = model(frame)
        heatmaps_l = model_l(frame)

    kp_coords = get_keypoints_from_heatmap_batch_maxpool(
        heatmaps[:, :-1, :, :],
    )
    line_coords = get_keypoints_from_heatmap_batch_maxpool_l(
        heatmaps_l[:, :-1, :, :],
    )

    kp_dict = coords_to_dict(
        kp_coords,
        threshold=kp_threshold,
    )
    lines_dict = coords_to_dict(
        line_coords,
        threshold=line_threshold,
    )
    final_dict = complete_keypoints(
        kp_dict,
        lines_dict,
        w=w,
        h=h,
        normalize=True,
    )

    cam.update(final_dict[0])
    final_params_dict = cam.heuristic_voting()

    return final_params_dict


def get_map_point(point, P):
    point = np.linalg.inv(P) @ np.array(point)
    point = point/point[2]
    point[0] += 105 / 2
    point[1] += 68 / 2

    return (point[0]/105, point[1]/68)


def project(P, coords, h, w):
    pts = [get_map_point([(x1 + x2) / 2, y2, 1], P)
           for x1, _, x2, y2 in coords]

    edges = [(0, 0, 1), (0, h, 1), (w, h, 1), (w, 0, 1)]
    edges = [get_map_point(edge, P) for edge in edges]

    return pts, edges


def process_input(input, coords, model, model_l, kp_threshold, line_threshold):
    frame_height = input.shape[0]
    frame_width = input.shape[1]

    cam = FramebyFrameCalib(
        iwidth=frame_width, iheight=frame_height, denormalize=True
    )

    final_params_dict = inference(
        cam, input, model, model_l, kp_threshold, line_threshold
    )

    if final_params_dict is not None:
        P = projection_from_cam_params(final_params_dict)

        P_reduced = np.array([
            [P[0][0], P[0][1], P[0][3]],
            [P[1][0], P[1][1], P[1][3]],
            [P[2][0], P[2][1], P[2][3]],
        ])
        pts, edges = project(P_reduced, coords, frame_height, frame_width)

    else:
        pts, edges = [], []

    return pts, edges


def inf_main(input, coords, kp_threshold=0.1486, line_threshold=0.3880, device=DEVICE):
    cfg = yaml.safe_load(open('tracking/yml/hrnetv2_w48.yaml', 'r'))
    cfg_l = yaml.safe_load(open('tracking/yml/hrnetv2_w48_l.yaml', 'r'))

    weights_kp = 'models/SV_FT_WC14_kp'
    weights_line = 'models/SV_FT_WC14_lines'

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

    pts, edges = process_input(
        input,
        coords,
        model,
        model_l,
        kp_threshold,
        line_threshold,
    )

    return pts, edges
