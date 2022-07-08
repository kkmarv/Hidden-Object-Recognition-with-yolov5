# Usage

- [Inference](#inference)
- [Evaluation](#evaluation)
- [Training](#training)

## Inference

### Prerequisites

It is expected that yolov5 is installed on the same level as the repos root dir (see illustration below).  
If you'd like to install or already have it installed elsewhere, see _Optional Arguments_ in the next section.

```
├── wimmelbilder-mit-yolov5
│   ├── datasets
│   ├── model
│   ├── src
│   ...
├── yolov5
│   └── ...
```

### Infer

First, open a terminal inside the repos root directory, then run

```shell
python src/inference/predict.py input_path
```

With `input_path` being a path to a single image or a directory of images on which to infer on.

<details><summary>Optional Arguments</summary>
  <ul>
    <li><code>--output_path</code> Specifies a directory in which the prediction images with visible bounding boxes will be saved. It won't be used if not specified.</li>
    <li><code>--yolov5_path</code> Use this to point to yolo's root dir.<br></li>
    <li><code>--weights_path</code> Use this to change the weights which will be used for inference.</li>
    <li><code>--team_name</code> Defaults to 'Tieeeeeeeeeeem'.</li>
  </ul>
</details>

### Results

The Inference will produce a `.csv` file for each image inside the `input_path` containing labels in yolov5 format. See
below for a short description.  
The file will be named after `image_name.team_name.csv`. For example, when inference is made on an image `x.png`, the
resulting `.csv` file will be called `x.Tieeeeeeeeeeem.csv` since `team_name` defaults to 'Tieeeeeeeeeeem'.

Additionally, if `--output_path` is specified, a directory containing images with visible bounding boxes will be
created at the specified path.

#### Format

| Parameter  | Description                                                 |
|------------|-------------------------------------------------------------|
| **Object** | [**Object ID**](#object-ids)                                |
| **x**      | Center x-position of the label. Normalized to image width.  |
| **y**      | Center y-position of the label. Normalized to image height. |
| **w**      | Normalized label width.                                     |
| **h**      | Normalized label height.                                    |

#### Object IDs

| ObjectId | ObjectType    |
|----------|---------------|
| 1        | Yoda          |
| 2        | Bagger        |
| 3        | Croissant     |
| 4        | Banane        |
| 5        | Brokkoli      |
| 6        | Getraenkedose |
| 7        | Leuchtturm    |
| 8        | Waldo         |
| 9        | Fussball      |
| 10       | W20           |

## Evaluation

For evaluation, you'll need Prof. Hänig's [**Wimmelbild
Generator**](https://gitlab.hs-anhalt.de/ki/lehre/modul-kuenstliche-intelligenz/praktikum-ss2022/wimmelbild-generator).

Open a terminal inside the _Wimmelbild Generator_ root directory and run

```shell
python src/wimmelbild_generator/evaluation_cli.py input_path Tieeeeeeeeeeem
```

With `input_path` being the path to the same directory used when inferring.

That's it.

## Training

### Prerequisites

For this workflow to function as intended, you'll have to have Docker, the NVIDIA Container Toolkit, Nvidia Drivers
installed, and you'll need a yolov5 Docker image.
Instructions for all this can be found [**here**](https://github.com/ultralytics/yolov5/wiki/Docker-Quickstart).

These steps will suffice to give you a working yolov5 image, but to fully use our Augmentation Pipeline, you'll need
a modified version of this image, which needs some manual manipulation. If you'd like to, you can:

<details><summary><b>Build the image yourself</b></summary>

After completing the above steps, we need to enable an augmentation library called `albumentations`.
This is achieved by running the previously downloaded image in interactive mode, so we can alter some files.

### 1) Start the Docker container and make some changes

To start the container, type

```shell
docker run --ipc=host -it --gpus all ultralytics/yolov5:latest  
```

You should be inside the docker container now. Now you have to manipulate some files:

- First, use any text editor to
  uncomment [line 38](https://github.com/ultralytics/yolov5/blob/master/requirements.txt#L38) inside
  the  `requirements.txt`.
  - Save and close the file afterwards.
- Then use the same editor to
  remove [lines 24-31](https://github.com/ultralytics/yolov5/blob/master/utils/augmentations.py#L24-L31)
  from `utils/augmentations.py`.
- Now paste the following in its place and save and close the file afterwards.

```python
T = [
  A.Blur(p=0.4, blur_limit=(3, 20)),
  A.ISONoise(p=0.4, intensity=(0.5, 2.0))]
```

Exit the container with

```shell
exit
```

### 2) Create an image from the altered container

Run

```shell
docker ps -a
```

and look for your container. Use the `IMAGE` column to identify it.  
With the container ID, use the following step to create the image.

```shell
docker commit [YOUR_CONTAINER_ID] ultralytics/yolov5:albumentations
```

</details>

### Train

Having a terminal open inside the repos root dir, type

```shell
src/train/run_yolo_docker.sh
```

which will automatically download the full training set from Roboflow, create a validation set from it and start the
yolov5 Docker container to start training on 2 GPUs.  
The script `run_yolo_docker.sh` is by far not flexible. It's intended for use on our own training machine only!

When the training is finished, you'll find the results in `runs/train/`.

#### Training Parameters Used

| Parameter          | Value                                               |
|--------------------|-----------------------------------------------------|
| Epochs             | 300                                                 |
| Batch Size         | 16 (8 per GPU)                                      |
| Image Size         | 640                                                 |
| Pretrained Weights | yolov5x.pt                                          |
| Hyperparameter     | hyp.HiddenObject.yaml + Blur & ISO (Albumentations) |
