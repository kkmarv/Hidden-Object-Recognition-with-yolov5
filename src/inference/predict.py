import os
import torch

# used for typing only
from pandas.core.frame import DataFrame


def is_valid_image_file(file_name: str) -> bool:
    return file_name.endswith('jpg') or file_name.endswith('jpeg') or file_name.endswith('png')


def convert_to_haenig(results_df: DataFrame) -> DataFrame:
    """Yep. Converts to Hänig."""
    results_df.rename(
        columns={'class': 'Object', 'xcenter': 'x', 'ycenter': 'y', 'width': 'w', 'height': 'h'},
        inplace=True
    )
    results_df.replace({
        'Object': {
            0: 2,  # Bagger -> 2
            1: 4,  # Banane -> 4
            2: 5,  # Brokkoli -> 5
            4: 9,  # Fussball -> 9
            5: 6,  # Getraenkedose ->  6
            6: 7,  # Leuchtturm -> 7
            7: 10,  # W20 -> 10
            9: 1  # Yoda -> 1
        }
    }, inplace=True)
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

    # save resulting images
    results.save(save_dir=model_output_path)

    # save resulting csv files
    digits = len(str(len(results)))
    for idx, result_df in enumerate(results.xywhn):
        convert_to_haenig(result_df).to_csv(
            f'{model_output_path}/image{str(idx).zfill(digits)}.csv', index=False
        )


if __name__ == '__main__':
    from cli import ARGS

    model_input_path = ARGS.input_path
    model_output_path = ARGS.output_path
    yolov5_path = ARGS.yolov5_path
    weights_path = ARGS.weights_path

    main()
