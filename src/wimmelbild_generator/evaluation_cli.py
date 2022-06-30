import argparse
import os

import pandas as pd

from src.wimmelbild_generator import evaluation
from src.wimmelbild_generator.generator import WimmelbildGenerator

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Wimmelbild Object Detection Evaluation Argument Parser')
    parser.add_argument('input_path', type=str, help='path of the input directory')
    parser.add_argument('group', type=str, help='name of the group')
    args = parser.parse_args()

    tp_total, fp_total, fn_total, gt_total = 0, 0, 0, 0
    for root, _, files in os.walk(args.input_path):
        for file in files:
            if WimmelbildGenerator.is_valid_image_file(file):
                image_file_prefix = file[:file.rindex('.')]
                truth_df = pd.read_csv(os.path.join(args.input_path, f'{image_file_prefix}.csv'),
                                       encoding='utf-8')
                pred_df_path = os.path.join(args.input_path, f'{image_file_prefix}.{args.group}.csv')
                if os.path.exists(pred_df_path):
                    pred_df = pd.read_csv(pred_df_path, encoding='utf-8')
                else:
                    pred_df = pd.DataFrame(columns=['Object', 'x', 'y', 'w', 'h'])

                tp, fp, fn, gt = evaluation.evaluate(truth_df, pred_df)
                tp_total += tp
                fp_total += fp
                fn_total += fn
                gt_total += gt

    print(f'Final results for group: "{args.group}"')
    evaluation.print_evaluation_scores(tp_total, fp_total, fn_total, gt_total)
