#! /usr/bin/env python

import torch
import torch.nn as nn
import onnx
from onnxsim import simplify
from argparse import ArgumentParser


class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()

    def forward(self, x1y1x2y2, classid, score):
        x1y1x2y2_classid_score_cat = torch.cat([x1y1x2y2, classid, score], dim=1)
        return x1y1x2y2_classid_score_cat


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        '-o',
        '--opset',
        type=int,
        default=11,
        help='onnx opset'
    )
    args = parser.parse_args()

    model = Model()

    MODEL = f'nms_batchno_classid_x1y1x2y2_cat'

    onnx_file = f"{MODEL}.onnx"
    OPSET=args.opset

    x1 = torch.ones([1, 4], dtype=torch.float32)
    x2 = torch.ones([1, 1], dtype=torch.float32)
    x3 = torch.ones([1, 1], dtype=torch.float32)

    torch.onnx.export(
        model,
        args=(x1,x2,x3),
        f=onnx_file,
        opset_version=OPSET,
        input_names=['cat_x1y1x2y2','cat_classid','cat_score'],
        output_names=['x1y1x2y2_classid_score'],
        dynamic_axes={
            'cat_x1y1x2y2': {0: 'N'},
            'cat_classid': {0: 'N'},
            'cat_score': {0: 'N'},
            'x1y1x2y2_classid_score': {0: 'N'},
        }
    )
    model_onnx1 = onnx.load(onnx_file)
    model_onnx1 = onnx.shape_inference.infer_shapes(model_onnx1)
    onnx.save(model_onnx1, onnx_file)

    model_onnx2 = onnx.load(onnx_file)
    model_simp, check = simplify(model_onnx2)
    onnx.save(model_simp, onnx_file)

