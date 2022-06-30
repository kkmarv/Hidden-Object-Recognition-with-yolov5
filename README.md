# Usage

## Inference

### Prerequisites

It is expected that yolov5 is installed under the repos root dir.  
If you'd like to install it elsewhere, see _Optional Arguments_ in the next section.

### Infer

First, open a terminal inside the repos root directory, then run

```shell
python src/inference/predict.py input_path output_path
```

With

- `input_path` being a path to a single image or a directory of images on which to infer on.
- `output_path` being a directory in which the predictions will be saved.

<details><summary>Optional Arguments</summary>
  <ul>
    <li><code>--yolov5_path</code> If yolo isn't installed in the root dir, use this to point to yolo's root dir.<br></li>
    <li><code>--weights_path</code> Use this to be able to change the weights which will be used for inference.</li>
  </ul>
</details>

## Training

### Prerequisites

For this workflow to function as intended, you'll have to have Docker, the NVIDIA Container Toolkit and Nvidia Drivers
installed. Furthermore, you'll need a yolov5 Docker image.
Instructions for all this can be found [**here**](https://github.com/ultralytics/yolov5/wiki/Docker-Quickstart).

### Train

Have a terminal opened in the repos root dir, then type

```shell

````

# TODO

- image augmentation
    - blur
    - skew colors
    - rotation
    - scaling
- get the evaluation running
- documentation
    - inference
    - training