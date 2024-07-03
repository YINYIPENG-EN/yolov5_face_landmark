#-*-coding:utf-8-*-
# date:2019-05-20
# Author: Eric.Lee
# function: data iter

import glob
import math
import os
import random
import shutil
from pathlib import Path
from PIL import Image
# import matplotlib.pyplot as plt
from tqdm import tqdm
import cv2
import numpy as np
import torch
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from data_iter.data_agu import *
import shutil
import json

# 图像白化
def prewhiten(x):
    mean = np.mean(x)
    std = np.std(x)
    std_adj = np.maximum(std, 1.0 / np.sqrt(x.size))
    y = np.multiply(np.subtract(x, mean), 1 / std_adj)
    return y

# 图像亮度、对比度增强
def contrast_img(img, c, b):  # 亮度就是每个像素所有通道都加上b
    rows, cols, channels = img.shape
    # 新建全零(黑色)图片数组:np.zeros(img1.shape, dtype=uint8)
    blank = np.zeros([rows, cols, channels], img.dtype)
    dst = cv2.addWeighted(img, c, blank, 1-c, b)
    return dst

class LoadImagesAndLabels(Dataset):
    def __init__(self, ops, img_size=(224,224), flag_agu = False,fix_res = True,vis = False):
        print('img_size (height,width) : ',img_size[0],img_size[1])
        r_ = open(ops.train_list,'r')
        lines = r_.readlines()
        idx = 0
        file_list = []
        landmarks_list = []
        for line in lines:
            # print(line)
            msg = line.strip().split(' ')
            idx += 1
            print('idx-',idx,' : ',len(msg))
            landmarks = msg[0:196]
            bbox = msg[196:200]
            attributes = msg[200:206]
            img_file = msg[206]
            print(img_file)
            pts = []
            global_dict_landmarks = {} # 全局坐标系坐标
            for i in range(int(len(landmarks)/2)):
                x = float(landmarks[i*2+0])
                y = float(landmarks[i*2+1])
                pts.append([x,y])


            landmarks_list.append(pts)
            file_list.append(ops.images_path+img_file)

        self.files = file_list
        self.landmarks = landmarks_list
        self.img_size = img_size
        self.flag_agu = flag_agu
        self.fix_res = fix_res
        self.vis = vis

    def __len__(self):
        return len(self.files)

    def __getitem__(self, index):
        img_path = self.files[index]
        pts = self.landmarks[index]
        img = cv2.imread(img_path)  # BGR
        if self.flag_agu == True:
            left_eye = np.average(pts[60:68], axis=0)
            right_eye = np.average(pts[68:76], axis=0)

            angle_random = random.randint(-36,36)
            # 返回 crop 图 和 归一化 landmarks
            img_, landmarks_  = face_random_rotate(img, pts, angle_random, left_eye, right_eye,
                fix_res = self.fix_res,img_size = self.img_size,vis = False)
        if self.flag_agu == True:
            if random.random() > 0.5:
                c = float(random.randint(50,150))/100.
                b = random.randint(-20,20)
                img_ = contrast_img(img_, c, b)
        if self.flag_agu == True:
            if random.random() > 0.7:
                # print('agu hue ')
                img_hsv=cv2.cvtColor(img_,cv2.COLOR_BGR2HSV)
                hue_x = random.randint(-10,10)
                # print(cc)
                img_hsv[:,:,0]=(img_hsv[:,:,0]+hue_x)
                img_hsv[:,:,0] =np.maximum(img_hsv[:,:,0],0)
                img_hsv[:,:,0] =np.minimum(img_hsv[:,:,0],180)#范围 0 ~180
                img_=cv2.cvtColor(img_hsv,cv2.COLOR_HSV2BGR)
        if self.flag_agu == True:
            if random.random() > 0.8:
                img_ = img_agu_channel_same(img_)
        if self.vis == True:
            cv2.namedWindow('crop',0)
            cv2.imshow('crop',img_)
            cv2.waitKey(1)
        img_ = img_.astype(np.float32)
        img_ = (img_-128.)/256.
        img_ = img_.transpose(2, 0, 1)
        landmarks_ = np.array(landmarks_).ravel()
        return img_,landmarks_
