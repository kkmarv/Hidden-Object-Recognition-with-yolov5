#!/usr/bin/env sh

root_dir=$(pwd)
dataset_dir="$root_dir"/datasets
train_cmd="python -m torch.distributed.run --nproc_per_node 2 train.py --img 640 --batch-size 64 --epochs 300 --data ../datasets/HiddenObject.yaml --weights yolov5s.pt --device 0,1"
evolve_cmd="for i in 0 1; do nohup python train.py --img 640 --epochs 10 --data ../datasets/HiddenObject.yaml --weights yolov5s.pt --cache --evolve --device \$i > evolve_gpu_\$i.log & done"

printf 'Downloading dataset...\n\n'
sleep 1

createValidationSet() {
  counter=0
  mkdir -p "$dataset_dir/$1/valid/images" "$dataset_dir/$1/valid/labels"
  for img in "$dataset_dir"/"$1"/train/images/*; do
    if [ $((counter % 4)) -eq 0 ]; then                                                    # move every 4th image to validation set by:
      filename=$(basename -- "$img")                                                       # getting an images file name,
      mv "$img" "$dataset_dir/$1/valid/images/"                                            # moving the image to validation set
      mv "$dataset_dir/$1/train/labels/${filename%.*}.txt" "$dataset_dir/$1/valid/labels/" # and moving its label too
    fi
    counter=$((counter += 1))
  done
  printf '\nCreated validation set at %s\n' "$dataset_dir"/"$1"/valid/
}

download() {
  download_dir="$dataset_dir/$2"
  curl -L "$1" >roboflow.zip                  # download the file at given link and save it to temporary zip file
  unzip -u -o roboflow.zip -d "$download_dir" # unzip file contents to given dir
  rm roboflow.zip                             # remove temporary zip file
  createValidationSet "$2"
}

# get dataset - contains confidential keys DO NOT SHARE!
download "https://app.roboflow.com/ds/UccvP21HOz?key=fBv59FvVxz" complete

printf 'Downloads finished.\n'
printf 'Starting yolov5 Docker container...\n'

run yolov5 docker
sudo docker run --ipc=host -it --gpus all \
  -v "$dataset_dir":/usr/src/datasets \
  -v "$root_dir"/runs:/usr/src/app/runs ultralytics/yolov5:latest \
  bash -c "wandb disabled && $train_cmd"
