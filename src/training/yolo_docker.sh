# Train and Evolve script by Marvin Kästing for yolov5 Docker

SCRIPT_DIR=$(pwd)
DATASET_DIR=$SCRIPT_DIR/datasets

# Create a validation set by selecting every 4th image (25%) from dataset
createValidationSet() {
  counter=0
  mkdir -p "$DATASET_DIR/$1/valid/images" "$DATASET_DIR/$1/valid/labels"
  for img in "$DATASET_DIR"/"$1"/train/images/*; do
    # move every 4th image to validation set
    if [ $((counter % 4)) -eq 0 ]; then
      filename=$(basename -- "$img")                                                       # get the images file name
      mv "$img" "$DATASET_DIR/$1/valid/images/"                                            # move image
      mv "$DATASET_DIR/$1/train/labels/${filename%.*}.txt" "$DATASET_DIR/$1/valid/labels/" # move its label too
    fi
    counter=$((counter += 1)) # increment
  done
  printf '\nCreated validation set at %s\n' "$DATASET_DIR"/"$1"/valid/
}

# Download a zip file from roboflow.com - This set should contain 100% training images
downloadDataset() {
  downloadDir="$DATASET_DIR/$2"
  curl -L "$1" >roboflow.zip
  unzip -u -o roboflow.zip -d "$downloadDir"
  rm roboflow.zip
  createValidationSet "$2"
}

# Training on 2 GPUs
train() {
  sudo docker run -it --ipc=host --gpus all \
    -v "$DATASET_DIR":/usr/src/datasets \
    -v "$SCRIPT_DIR"/runs:/usr/src/app/runs \
    ultralytics/yolov5:albumentations \
    bash -c "wandb disabled && python -m torch.distributed.run --nproc_per_node 2 train.py \
    --epochs 300 \
    --weights  yolov5x.pt \
    --data ../datasets/HiddenObject.yaml \
    --hyp ../datasets/hyp.HiddenObject.yaml \
    --imgsz 640 \
    --batch-size 16 \
    --workers 8 \
    --device 0,1"
}

# Hyperparameter Evolution on a single GPU
evolve() {
  sudo docker run -it --ipc=host --gpus all \
    -v "$DATASET_DIR":/usr/src/datasets \
    -v "$SCRIPT_DIR"/runs:/usr/src/app/runs \
    ultralytics/yolov5:albumentations \
    bash -c "wandb disabled && python train.py \
      --epochs 10 \
      --weights ./runs/train/exp77/weights/last.pt \
      --data ../datasets/HiddenObject.yaml \
      --hyp ../datasets/hyp.HiddenObject.yaml \
      --imgsz 640 \
      --batch-size 64 \
      --workers 8 \
      --device 0 \
      --evolve"
}

printf 'Downloading dataset...\n\n'
# downloadDataset "https://app.roboflow.com/ds/lXKrPuA4P2?key=M1kKwXHWCD" complete # 1280px
downloadDataset "https://app.roboflow.com/ds/FCPyLAaEo9?key=jD8JeJl3fz" complete # 640px
printf 'Downloads finished.\n\n'

printf 'Starting yolov5...\n'
train
