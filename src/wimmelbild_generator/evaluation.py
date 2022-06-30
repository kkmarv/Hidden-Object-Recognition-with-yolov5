from typing import Tuple

import numpy as np
import pandas as pd
from shapely.geometry import box


def evaluate(true_df: pd.DataFrame, pred_df: pd.DataFrame, iou_value: float = 0.5) -> Tuple[int, int, int, int]:
    object_types = set(true_df['Object'].unique()).union(pred_df['Object'].unique())

    tp, fp, fn = 0, 0, 0
    for object_type in object_types:
        tp_type, fp_type, fn_type = evaluate_object_type(true_df[true_df['Object'] == object_type],
                                                         pred_df[pred_df['Object'] == object_type], iou_value)
        tp += tp_type
        fp += fp_type
        fn += fn_type

    print_evaluation_scores(tp, fp, fn, len(true_df))
    return tp, fp, fn, len(true_df)


def evaluate_object_type(true_df: pd.DataFrame, pred_df: pd.DataFrame, iou_value: float = 0.5):
    # 'Object', 'x', 'y', 'w', 'h'

    # Using predicted output as the reference
    prob1 = []
    for _, prediction in pred_df.iterrows():
        predicted_box = df_row_to_box(prediction)
        cont = []
        for _, true in true_df.iterrows():
            truth_box = df_row_to_box(true)
            iou = truth_box.intersection(predicted_box).area / truth_box.union(predicted_box).area
            cont.append(iou)
        prob1.append(cont)

    fp = 0
    for t in prob1:
        if check_less(t, iou_value):
            fp = fp + 1

    prob2 = []
    # loop through each ground truth instance
    for _, true in true_df.iterrows():
        truth_box = df_row_to_box(true)
        cont = []
        # merge up the ground truth instance against prediction
        # to determine the IoU
        for _, prediction in pred_df.iterrows():
            predicted_box = df_row_to_box(prediction)
            iou = truth_box.intersection(predicted_box).area / truth_box.union(predicted_box).area
            cont.append(iou)
        # probability of a given prediction to be contained in a
        # ground truth instance
        prob2.append(cont)
    fn = 0
    tp = 0
    for t in prob2:
        if np.sum(t) == 0:
            fn = fn + 1
        elif not check_less(t, iou_value):
            tp = tp + 1

    return tp, fp, fn


def check_less(list1, val):
    return all(x <= val for x in list1)


def df_row_to_box(row):
    return box(row['x'] - 0.5 * row['w'], row['y'] - 0.5 * row['h'],
               row['x'] + 0.5 * row['w'], row['y'] + 0.5 * row['h'])


def print_evaluation_scores(tp: int, fp: int, fn: int, ground_truth_elements: int):
    print("TP:", tp, "\t FP:", fp, "\t FN:", fn, "\t GT:", ground_truth_elements)
    if tp + fp == 0:
        precision = 0
    else:
        precision = round(tp / (tp + fp), 3)
    if tp + fn == 0:
        recall = 0
    else:
        recall = round(tp / (tp + fn), 3)
    if precision + recall == 0:
        f1 = 0
    else:
        f1 = round(2 * ((precision * recall) / (precision + recall)), 3)
    print(f'Precision: {precision}\t Recall: {recall}\t F1 score: {f1}')
