import os
import torch

# used for typing only
from pandas import DataFrame


def is_valid_image_file(file_name: str) -> bool:
    return file_name.endswith('jpg') or file_name.endswith('jpeg') or file_name.endswith('png')


def convert_to_haenig(results_df: DataFrame) -> DataFrame:
    """Yep. Converts to Hänig."""
    results_df.rename(
        columns={'class': 'Object', 'xcenter': 'x', 'ycenter': 'y', 'width': 'w', 'height': 'h'},
        inplace=True
    )
    return results_df[['Object', 'x', 'y', 'w', 'h']]


def main() -> None:
    # load the model
    model = torch.hub.load(yolov5_path, 'custom', source='local', path=weights_path)

    # find images
    images: list = []
    for root, _, files in os.walk(model_input_path):
        for file in files:
            if is_valid_image_file(file):
                images.append(os.path.join(root, file))

    # do inference
    results = model(images).pandas()  # or .show(), .save(), .crop(), .pandas(), etc

    # save resulting images and csv files
    results.save(save_dir=model_output_path)
    for idx, result_df in enumerate(results.xywhn):
        convert_to_haenig(result_df).to_csv(f'{model_output_path}/{idx}.csv', index=False)


if __name__ == '__main__':
    from cli import ARGS

    model_input_path = ARGS.input_path
    model_output_path = ARGS.output_path
    yolov5_path = ARGS.yolov5_path
    weights_path = ARGS.weights_path

    main()
