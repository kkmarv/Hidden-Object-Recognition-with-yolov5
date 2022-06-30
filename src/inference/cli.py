import os.path
import argparse


class ARGS:
    """A namespace object containing all arguments parsed."""
    input_path: str
    output_path: str
    yolov5_path: str
    weights_path: str


parser = argparse.ArgumentParser()

# positional arguments
parser.add_argument('input_path', type=str,
                    help='Path to model input. Can be either a single image or a directory. Valid image types are: .png, .jpeg, .jpg')
parser.add_argument('output_path', type=str,
                    help='Path to model output dir. Will be created along the way if it not exists.')

# optional arguments
parser.add_argument('--yolov5_path', type=str, help='Path to yolov5 root dir.')
parser.add_argument('--weights_path', type=str, help='Path to custom yolov5 weights (.pt).')

parser.set_defaults(
    yolov5_path='./yolov5/',
    weights_path='./model/best.pt'
)

parser.parse_args(namespace=ARGS)

# argument validation
if not os.path.exists(ARGS.input_path):
    parser.error(f'Input path not found: {ARGS.input_path}')

# output path creation
os.makedirs(ARGS.output_path, exist_ok=True)
