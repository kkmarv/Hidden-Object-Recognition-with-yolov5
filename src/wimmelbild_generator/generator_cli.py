import argparse
import os.path

import cv2

from src.wimmelbild_generator.generator import WimmelbildGenerator

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Wimmelbild Generator Argument Parser')
    parser.add_argument('input', type=str, help='path of the input directory')
    parser.add_argument('output', type=str, help='path of the output directory')
    parser.add_argument('images', type=int, help='number of images that will be generated')
    parser.add_argument('--min_objects', type=int, default=5, help='minimum number of objects per image')
    parser.add_argument('--max_objects', type=int, default=25, help='maximum number of objects per image')
    parser.add_argument('--min_object_size', type=float, default=0.0025, help='minimum relative object size')
    parser.add_argument('--max_object_size', type=float, default=0.05, help='maximum relative object size')
    parser.add_argument('--object_types', type=str, default='data/object_types.csv',
                        help='dataframe containing object types definitions')
    args = parser.parse_args()

    generator = WimmelbildGenerator(args.input,
                                    args.min_objects, args.max_objects,
                                    args.min_object_size, args.max_object_size,
                                    args.object_types)

    os.makedirs(args.output, exist_ok=True)
    digits = len(str(args.images))
    for i in range(args.images):
        image, objects = generator.generate()
        cv2.imwrite(os.path.join(args.output, f'image{str(i).zfill(digits)}.jpg'), image)
        objects.to_csv(os.path.join(args.output, f'image{str(i).zfill(digits)}.csv'), index=False)
