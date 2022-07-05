#!/usr/bin/env sh

scriptDir=$(pwd)
datasetDir=$scriptDir/datasets
train="python -m torch.distributed.run --nproc_per_node 2 train.py --img 640 --batch-size 64 --epochs 300 --data ../datasets/HiddenObject.yaml --hyp ../datasets/hyp.HiddenObject.yaml --weights yolov5s.pt --device 0,1"
evolve="for i in 0 1; do nohup python train.py --img 640 --epochs 10 --data ../datasets/HiddenObject.yaml --weights yolov5s.pt --cache --evolve --device \$i > evolve_gpu_\$i.log & done"

printf 'Starting yolov5 docker container...\n'
printf 'Downloading dataset...\n\n'; sleep 1


createValidationSet () {
  counter=0
  mkdir -p "$datasetDir/$1/valid/images" "$datasetDir/$1/valid/labels"
  for img in "$datasetDir"/"$1"/train/images/*; do
    # move every 4th image to validation set
    if [ $((counter%4)) -eq 0 ]; then
      filename=$(basename -- "$img") # get the images file name
      mv "$img" "$datasetDir/$1/valid/images/" # move image
      mv "$datasetDir/$1/train/labels/${filename%.*}.txt" "$datasetDir/$1/valid/labels/" # move its label too
    fi; counter=$((counter+=1))
  done
  printf '\nCreated validation set at %s\n' "$datasetDir"/"$1"/valid/
}

download () {
  downloadDir="$datasetDir/$2"
  curl -L "$1" > roboflow.zip; unzip -u -o roboflow.zip -d "$downloadDir"; rm roboflow.zip;
  createValidationSet "$2"
}

# get dataset - contains confidential keys DO NOT SHARE!
download "https://app.roboflow.com/ds/fsEElRHkPO?key=z60vtBY30a" complete

printf 'Downloads finished.\n'; sleep 1

# run yolov5 docker
sudo docker run --ipc=host -it --gpus all \
-v "$datasetDir":/usr/src/datasets \
-v "$scriptDir"/runs:/usr/src/app/runs ultralytics/yolov5:albumentations \
bash -c wandb disabled && "$train"
