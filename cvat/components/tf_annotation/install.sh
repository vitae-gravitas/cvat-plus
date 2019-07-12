#!/bin/bash
#
# Copyright (C) 2018 Intel Corporation
#
# SPDX-License-Identifier: MIT
#
set -e

cd ${HOME} && \
wget -O model.tar.gz http://download.tensorflow.org/models/object_detection/faster_rcnn_inception_resnet_v2_atrous_coco_2018_01_28.tar.gz && \
tar -xzf model.tar.gz && rm model.tar.gz && \
mv faster_rcnn_inception_resnet_v2_atrous_coco_2018_01_28 ${HOME}/rcnn && cd ${HOME} && \
mv rcnn/frozen_inference_graph.pb rcnn/inference_graph.pb

if [[ "$CUDA_SUPPORT" = "yes" ]]
then
    pip3 install --no-cache-dir tensorflow-gpu==1.7.0
else
    pip3 install --no-cache-dir tensorflow==1.7.0
fi
