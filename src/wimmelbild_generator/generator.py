import os.path
from typing import Tuple, Set, Dict, List

import cv2
import numpy as np
import pandas as pd
from shapely.geometry import box


class WimmelbildGenerator:
    def __init__(self, path: str,
                 min_objects: int, max_objects: int,
                 min_object_size: float, max_object_size: float,
                 object_types_path: str):
        self.background_images = []
        for root, _, files in os.walk(os.path.join(path, 'data', 'background')):
            for file in files:
                if self.is_valid_image_file(file):
                    image = cv2.imread(os.path.join(root, file))
                    self.background_images.append(image)

        self.object_images: Dict[str, List[np.ndarray]] = {}
        for root, dirs, _ in os.walk(os.path.join(path, 'data', 'objects')):
            for object_dir in dirs:
                self.object_images[object_dir] = []
                for object_root, _, files in os.walk(os.path.join(root, object_dir)):
                    for file in files:
                        if self.is_valid_image_file(file):
                            image = cv2.imread(os.path.join(object_root, file), cv2.IMREAD_UNCHANGED)
                            self.object_images[object_dir].append(image)

        self.min_objects = min_objects
        self.max_objects = max_objects
        self.min_object_size = min_object_size
        self.max_object_size = max_object_size
        self.object_types = {}
        for _, line in pd.read_csv(path + object_types_path, encoding='utf-8', sep=';').iterrows():
            self.object_types[line['ObjectType']] = line['ObjectId']

    def generate(self) -> Tuple[np.ndarray, pd.DataFrame]:
        image = self.random_background()
        image_df = pd.DataFrame(columns=['Object', 'x', 'y', 'w', 'h'])

        num_objects = np.random.randint(self.min_objects, self.max_objects + 1)
        while len(image_df) < num_objects:
            image = self.place_object(image, image_df)

        return image, image_df[image_df['Object'] != -1]

    def random_background(self) -> np.ndarray:
        return np.copy(self.background_images[np.random.choice(len(self.background_images))])

    def place_object(self, image: np.ndarray, image_df: pd.DataFrame) -> np.ndarray:
        object_type = np.random.choice(np.asarray(list(self.object_images)))
        object_image = self.object_images[object_type][np.random.choice(len(self.object_images[object_type]))]
        object_image = self.rescale_image(image, object_image)
        object_image = self.skew_colors(object_image)
        object_image = self.blur_image(object_image)
        object_image, object_mask = self.rotate_image(object_image, np.random.normal(0, 60))

        for _ in range(10):
            x = np.random.randint(image.shape[1] - object_image.shape[1])
            y = np.random.randint(image.shape[0] - object_image.shape[0])
            if not self.overlaps(image_df, image, object_image, x, y):
                self.append_to_image_df(image_df, image, object_type, object_image, x, y)
                return self.copy_image(image, object_image, object_mask, x, y)

        return image

    def rescale_image(self, image: np.ndarray, object_image: np.ndarray) -> np.ndarray:
        size_factor = np.random.normal(loc=0.5, scale=0.5 / 3)
        size_factor = max(0, size_factor)
        size_factor = min(1, size_factor)
        target_size = (self.max_object_size - self.min_object_size) * size_factor + self.min_object_size
        actual_size = (object_image.shape[0] * object_image.shape[1]) / (image.shape[0] * image.shape[1])
        scaling_factor = np.sqrt(target_size / actual_size)
        target_width = int(object_image.shape[1] * scaling_factor)
        target_height = int(object_image.shape[0] * scaling_factor)
        return cv2.resize(object_image, (target_width, target_height), interpolation=cv2.INTER_AREA)

    def append_to_image_df(self, image_df: pd.DataFrame, image: np.ndarray,
                           object_type: str, object_image: np.ndarray, x: int, y: int):
        image_w = image.shape[1]
        image_h = image.shape[0]

        w = object_image.shape[1]
        h = object_image.shape[0]

        object_df_index = len(image_df)
        if object_type in self.object_types:
            image_df.at[object_df_index, 'Object'] = self.object_types[object_type]
        else:
            image_df.at[object_df_index, 'Object'] = -1
        image_df.at[object_df_index, 'x'] = (x + 0.5 * w) / image_w
        image_df.at[object_df_index, 'y'] = (y + 0.5 * h) / image_h
        image_df.at[object_df_index, 'w'] = w / image_w
        image_df.at[object_df_index, 'h'] = h / image_h

    @staticmethod
    def blur_image(object_image: np.ndarray) -> np.ndarray:
        kernel_size = np.random.randint(10)
        kernel_size = 2 * kernel_size + 1
        return cv2.blur(object_image, (kernel_size, kernel_size))

    @staticmethod
    def skew_colors(object_image: np.ndarray) -> np.ndarray:
        color_mask = np.random.normal(1., 0.15, object_image.shape)
        if color_mask.shape[2] == 4:
            color_mask[:, :, 3] = 1.
        skewed_image = np.multiply(object_image, color_mask)
        skewed_image = np.minimum(skewed_image, np.ones(object_image.shape) * 255)
        skewed_image = np.maximum(skewed_image, np.zeros(object_image.shape))
        return skewed_image

    @staticmethod
    def copy_image(image: np.ndarray, object_image: np.ndarray, object_mask: np.ndarray, x: int, y: int):
        if x >= image.shape[1] or y >= image.shape[0]:
            raise ValueError(f'x ({x}) or y ({y}) do not match target image shape ({image.shape})')

        if x + object_image.shape[1] > image.shape[1]:
            object_image = object_image[:, :image.shape[1] - x]

        if y + object_image.shape[0] > image.shape[0]:
            object_image = object_image[:image.shape[0] - y]

        if object_image.shape[2] < 4:
            object_image = np.concatenate(
                [
                    object_image,
                    np.ones((object_image.shape[0], object_image.shape[1], 1), dtype=object_image.dtype) * 255
                ],
                axis=2,
            )

        background_mask = object_image[..., 3:] / 255.0
        mask = np.multiply(background_mask, object_mask)

        object_image = object_image[..., :3]

        image[y:y + object_image.shape[0], x:x + object_image.shape[1]] = \
            (1.0 - mask) * image[y:y + object_image.shape[0], x:x + object_image.shape[1]] + mask * object_image

        return image

    @staticmethod
    def rotate_image(image: np.ndarray, angle: float) -> Tuple[np.ndarray, np.ndarray]:
        height, width = image.shape[:2]
        image_center = (width / 2, height / 2)

        rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.)

        # rotation calculates the cos and sin, taking absolutes of those.
        abs_cos = abs(rotation_mat[0, 0])
        abs_sin = abs(rotation_mat[0, 1])

        # find the new width and height bounds
        bound_w = int(height * abs_sin + width * abs_cos)
        bound_h = int(height * abs_cos + width * abs_sin)

        # subtract old image center (bringing image back to origo) and adding the new image center coordinates
        rotation_mat[0, 2] += bound_w / 2 - image_center[0]
        rotation_mat[1, 2] += bound_h / 2 - image_center[1]

        # rotate image with the new bounds and translated rotation matrix
        mask = np.ones(image.shape)
        rotated_image = cv2.warpAffine(image, rotation_mat, (bound_w, bound_h))
        rotated_mask = cv2.warpAffine(mask, rotation_mat, (bound_w, bound_h), borderValue=(0,))
        return rotated_image, np.expand_dims(rotated_mask[:, :, 0], -1)

    @staticmethod
    def is_valid_image_file(file_name: str) -> bool:
        return file_name.endswith('jpg') or file_name.endswith('jpeg') or file_name.endswith('png')

    def overlaps(self, image_df: pd.DataFrame, image: np.ndarray, object_image: np.ndarray, x: int, y: int) -> bool:
        image_w = image.shape[1]
        image_h = image.shape[0]
        w = object_image.shape[1]
        h = object_image.shape[0]

        x = (x + 0.5 * w) / image_w
        y = (y + 0.5 * h) / image_h
        w = w / image_w
        h = h / image_h

        for _, row in image_df.iterrows():
            if self.overlaps_box((row['x'], row['y'], row['w'], row['h']), (x, y, w, h)):
                return True

        return False

    def overlaps_box(self, tuple_a: Tuple[float, float, float, float],
                     tuple_b: Tuple[float, float, float, float]) -> bool:
        box_a = box(tuple_a[0] - 0.5 * tuple_a[2], tuple_a[1] - 0.5 * tuple_a[3],
                    tuple_a[0] + 0.5 * tuple_a[2], tuple_a[1] + 0.5 * tuple_a[3])
        box_b = box(tuple_b[0] - 0.5 * tuple_b[2], tuple_b[1] - 0.5 * tuple_b[3],
                    tuple_b[0] + 0.5 * tuple_b[2], tuple_b[1] + 0.5 * tuple_b[3])

        iou = box_a.intersection(box_b).area / box_a.union(box_b).area
        return iou >= 0.1
