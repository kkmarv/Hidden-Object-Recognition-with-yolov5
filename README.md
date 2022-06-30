# Usage

- First, open a terminal inside the repos root directory.
- Run `predict.py` with:
    - the first argument being a path to (an) image(s) which the model will infer on and
    - the second argument being directory path to which the models predictions will be saved.

**Hints**

- `predict.py` expects yolov5 in root dir by default. If yolo is installed in another location, use `--yolov5_path`

**TODO**

- image augmentation
- blur
- skew colors
- rotation
- scaling