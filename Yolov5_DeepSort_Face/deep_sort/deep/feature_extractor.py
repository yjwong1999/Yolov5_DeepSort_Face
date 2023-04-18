import os
import os.path as osp
import yaml
import time
import argparse

import torch
import torch.nn as nn
import torchvision.transforms as transforms

from tabulate import tabulate
from datetime import datetime

from opensphere.utils import fill_config ##### edited for pipeline
from opensphere.builder import build_dataloader, build_from_cfg ##### edited for pipeline
import cv2, logging
import numpy as np

def parse_args():
    parser = argparse.ArgumentParser(
            description='A PyTorch project for face recognition.')
    parser.add_argument('--config', 
            help='config files for project/models')
    args = parser.parse_args()

    return args

@torch.no_grad()
def get_feats(net, data, flip=True):
    # extract features from the original 
    # and horizontally flipped data
    feats = net(data)
    if flip:
        data = torch.flip(data, [3])
        feats += net(data)

    return feats.data.cpu()

@torch.no_grad()
def get_model(project_config, device):
    # parallel setting
    if device == 'cuda':
        # if multi gpu
        '''
        device_ids = os.environ['CUDA_VISIBLE_DEVICES']
        device_ids = list(range(len(device_ids.split(','))))
        '''
        # if single gpu
        os.environ['CUDA_VISIBLE_DEVICES'] = '0'
        device_ids = [0] 
    elif device == 'cpu':  
        os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
        device_ids = ['cpu']

    config = project_config + '/' + 'config.yml'
    with open(config, 'r') as f:
        config = yaml.load(f, yaml.SafeLoader)

    # build model
    bkb_net = build_from_cfg(
        config['model']['backbone']['net'],
        'model.backbone',
    )
    bkb_net = nn.DataParallel(bkb_net, device_ids=device_ids)
    if device == 'cuda':
        bkb_net = bkb_net.cuda()
    bkb_net.eval()

    # model paths and run test
    model_dir = project_config + '/models'
    save_iters = config['project']['save_iters']
    save_iter = save_iters[-1] # we take the last checkpoint as the model
    '''
    bkb_paths = [
        osp.join(model_dir, 'backbone_{}.pth'.format(save_iter))
        for save_iter in save_iters
    ]
    '''
    bkb_path = osp.join(model_dir, 'backbone_{}.pth'.format(save_iter))
        
    # load model parameters
    if device == 'cuda':
        bkb_net.load_state_dict(torch.load(bkb_path))
    elif device == 'cpu':
        bkb_net.load_state_dict(torch.load(bkb_path, map_location=torch.device('cpu') ))
    
    return bkb_net
    
    # collect features
    '''
    data = data.cuda()
    feats = get_feats(bkb_net, data)
    '''


class Extractor(object):
    def __init__(self, project_config, use_cuda=False):
        self.device = "cuda" if torch.cuda.is_available() and use_cuda else "cpu"
        self.input_width = 112
        self.input_height = 112

        self.model = get_model(project_config, device=self.device)
        self.model.to(self.device)
        self.model.eval()

        logger = logging.getLogger("root.tracker")
        logger.info("Selected model type: {}".format(project_config))
        self.size = (self.input_width, self.input_height)
        self.norm = transforms.Compose([
            transforms.ToTensor(),
            #transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])        

    def _preprocess(self, im_crops):
        """
        TODO:
            0. REMOVE transforms.Normalize			# done
            1. to float with scale from -1 to 1 		# done
            2. resize to (112, 112) 				# done
            3. concatenate to a numpy array
            3. to torch Tensor
        """
        def _resize(im, size):
            #return cv2.resize(im.astype(np.float32) / 255., size)
            # normalize first
            xi = im.astype(np.float32)
            xmin, xmax = 0, 255
            zi = 2 * ((xi - xmin) / (xmax - xmin)) - 1
            return cv2.resize(zi, size)

        im_batch = torch.cat([self.norm(_resize(im, self.size)).unsqueeze(
            0) for im in im_crops], dim=0).float()
        return im_batch

    def __call__(self, im_crops):
        im_batch = self._preprocess(im_crops)
        features = get_feats(self.model, im_batch)
        return features.cpu().numpy()
        '''
        with torch.no_grad():
            im_batch = im_batch.to(self.device)
            features = self.model(im_batch)
        return features.cpu().numpy()
        '''


if __name__ == '__main__':
    # get arguments and config
    args = parse_args()
    project_config = args.config
    
    img = [np.ones((112, 110, 3)), np.ones((112, 110, 3))]
    extr = Extractor(project_config)
    feature = extr(img)
    print(feature.shape)
