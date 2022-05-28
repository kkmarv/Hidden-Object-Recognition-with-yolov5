#!/usr/bin/env sh

scriptDir=$(pwd)
datasetsDir=./datasets

# get datasets - contains confidential keys DO NOT SHARE!
curl -L "https://app.roboflow.com/ds/3JqUkFazKy?key=gO8znJvhOO" > \
$datasetsDir/roboflow.zip; unzip $datasetsDir/roboflow.zip; rm $datasetsDir/roboflow.zip

curl -L "https://app.roboflow.com/ds/t9mXLVwSTE?key=pbKva5v9LR" > \
$datasetsDir/roboflow.zip; unzip $datasetsDir/roboflow.zip; rm $datasetsDir/roboflow.zip

curl -L "https://app.roboflow.com/ds/EzlBpUrlE0?key=hufaTQ7eg6" > \
$datasetsDir/roboflow.zip; unzip $datasetsDir/roboflow.zip; rm $datasetsDir/roboflow.zip

# run training inside docker
sudo docker run --ipc=host -it --gpus all \
-v "$scriptDir"/datasets:/usr/src/datasets \
-v "$scriptDir"/runs:/usr/src/app/runs ultralytics/yolov5:latest \
bash -c "pip install roboflow && python -m torch.distributed.run --nproc_per_node 2 ./train.py --img 640 --batch-size 64 --epochs 300 --data ../datasets/HiddenObject.yaml --weights yolov5s.pt --device 0,1"
