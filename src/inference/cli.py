import os.path
from argparse import ArgumentParser


class ARGS:
    """A namespace object containing all arguments parsed."""
    input_path: str
    output_path: str
    yolov5_path: str
    weights_path: str
    team_name: str


parser = ArgumentParser()

# positional arguments
parser.add_argument('input_path', type=str,
                    help='Path to model input. Can be either a single image or a directory. Valid image types are: .png, .jpeg, .jpg')

# optional arguments
parser.add_argument('--output_path', type=str,
                    help='Path to model output dir containing original images and their visible bounding boxes. Will be created along the way if it does not exist.')
parser.add_argument('--yolov5_path', type=str, help='Path to yolov5 root dir.')
parser.add_argument('--weights_path', type=str, help='Path to custom yolov5 weights (.pt).')
parser.add_argument('--team_name', type=str, help='Name of the team.')

parser.set_defaults(
    yolov5_path='../yolov5/',
    weights_path='./model/best.pt',
    team_name='Tieeeeeeeeeeem'  # don't judge pls
)

parser.parse_args(namespace=ARGS)

# argument validation
if not os.path.exists(ARGS.input_path):
    parser.error(f'Input path not found: {ARGS.input_path}')
if not os.path.exists(ARGS.yolov5_path):
    parser.error(f'Yolov5 path not found: {ARGS.yolov5_path}')
if not os.path.exists(ARGS.weights_path):
    parser.error(f'Weights path not found: {ARGS.weights_path}')

# output path creation
if ARGS.output_path:
    os.makedirs(ARGS.output_path, exist_ok=True)
