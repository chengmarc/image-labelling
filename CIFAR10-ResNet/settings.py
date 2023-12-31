# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
DATASET = "CIFAR10"
NET = "ResNet34"

BATCH_SIZE_TRAIN = 128
BATCH_SIZE_TEST = 16

EPOCH = 200
LEARNING_RATE = 0.1
MILESTONES = [60, 120, 160]
WARM = 1

USE_GPU = True
NUM_WORKERS = 4

