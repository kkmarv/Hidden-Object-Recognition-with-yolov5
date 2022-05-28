#!/usr/bin/env sh

scriptDir=$(pwd)
datasetDir=$scriptDir/datasets/

printf '\n'

# get dataset - contains confidential keys DO NOT SHARE!
curl -L "https://app.roboflow.com/ds/3JqUkFazKy?key=gO8znJvhOO" > \
roboflow.zip; unzip -u -o roboflow.zip -d "$datasetDir"; rm roboflow.zip

curl -L "https://app.roboflow.com/ds/t9mXLVwSTE?key=pbKva5v9LR" > \
roboflow.zip; unzip -u -o roboflow.zip -d "$datasetDir"; rm roboflow.zip

curl -L "https://app.roboflow.com/ds/EzlBpUrlE0?key=hufaTQ7eg6" > \
roboflow.zip; unzip -u -o roboflow.zip -d "$datasetDir"; rm roboflow.zip

# train in yolov5 docker
sudo docker run --ipc=host -it --gpus all \
-v "$datasetDir":/usr/src/datasets \
-v "$scriptDir"/runs:/usr/src/app/runs ultralytics/yolov5:latest \
bash -c "python -m torch.distributed.run --nproc_per_node 2 ./train.py --img 640 --batch-size 64 --epochs 300 --data ../datasets/HiddenObject.yaml --weights yolov5s.pt --device 0,1"
