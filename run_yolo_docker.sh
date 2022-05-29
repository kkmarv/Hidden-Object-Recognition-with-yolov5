#!/usr/bin/env sh

scriptDir=$(pwd)
datasetDir=$scriptDir/datasets
train="python -m torch.distributed.run --nproc_per_node 2 train.py --img 640 --batch-size 64 --epochs 300 --data ../datasets/HiddenObject.yaml --weights yolov5s.pt --device 0,1"
evolve="for i in 0 1; do nohup python train.py --img 640 --epochs 10 --data ../datasets/HiddenObject.yaml --weights yolov5s.pt --cache --evolve --device \$i > evolve_gpu_\$i.log & done"

printf 'Starting yolov5 docker container...\n'
printf 'Downloading dataset...\n\n'; sleep 1

download () { curl -L "$1" > roboflow.zip; unzip -u -o roboflow.zip -d "$datasetDir/$2"; rm roboflow.zip; printf '\n'; }

# get dataset - contains confidential keys DO NOT SHARE!
#download "https://app.roboflow.com/ds/3JqUkFazKy?key=gO8znJvhOO" banana
#download "https://app.roboflow.com/ds/t9mXLVwSTE?key=pbKva5v9LR" banana
#download "https://app.roboflow.com/ds/EzlBpUrlE0?key=hufaTQ7eg6" banana
download "https://app.roboflow.com/ds/fthEaj8GjD?key=mHqK5Kj2IS" excavator

printf 'Downloads finished.\n'; sleep 1

# run yolov5 docker
sudo docker run --ipc=host -it --gpus all \
-v "$datasetDir":/usr/src/datasets \
-v "$scriptDir"/runs:/usr/src/app/runs ultralytics/yolov5:latest \
bash -c "$evolve"
