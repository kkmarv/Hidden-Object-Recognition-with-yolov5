# Usage

## Inference

First, open a terminal inside the repos root directory. Then, run

```shell
python src/inference/predict.py input_path output_path
```

With

- `input_path` being a path to a single image or a directory of images.
- `output_path` being a directory in which the predictions will be saved.

<details><summary>Optional Arguments</summary>
  <ul>
    <li><code>--yolov5_path</code> It is expected that yolov5 is installed under the root dir. If yolo is installed in another location, use this.<br></li>
    <li><code>--weights_path</code> Determines the path to the weights which will be used.</li>
  </ul>
</details>

## Training

### Prerequisites

For this workflow to function as intended, you'll have to have Docker, the NVIDIA Container Toolkit, Nvidia Drivers
installed. Furthermore, you'll need a yolov5 Docker image.
Instructions for all this can be found [**here**](https://github.com/ultralytics/yolov5/wiki/Docker-Quickstart).

### Start training

Have a terminal opened in the repos root dir, then type

```shell

````

# TODO

- image augmentation
- blur
- skew colors
- rotation
- scaling