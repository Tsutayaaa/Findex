#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
heat_loader.py

该模块从 .npy 文件中提取热图数据（'heatmap_data'）及相关元数据，
返回原始数组格式及配置信息，支持后期重新绘制叠加热图。

用法（脚本运行）：
    python heat_loader.py --npy_file path/to/heatmap_data.npy

用法（模块调用）：
    from heat_loader import HeatmapLoader
    loader = HeatmapLoader("path/to/heatmap_data.npy")
    print(loader.heatmap.shape)
"""

import numpy as np
import argparse
import os

class HeatmapLoader:
    """
    HeatmapLoader 用于加载 .npy 文件中的热图数据（'heatmap_data'）及元数据，
    返回原始数组及其他配置信息，为后期绘制叠加热图提供输入。
    """
    def __init__(self, filepath):
        """初始化加载器，加载并预处理 .npy 文件"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在：{filepath}")
        self.data = np.load(filepath, allow_pickle=True)
        # 检查是否为字典，否则假设是纯数组（旧版兼容）
        if isinstance(self.data, dict):
            self.data = self.data
        elif self.data.ndim == 0:  # 处理 .item() 的情况
            self.data = self.data.item()
        else:
            self.data = {'heatmap_data': self.data}  # 旧版纯数组
        self._processed = self._preprocess()

    def _preprocess(self):
        """预处理数据，提取所有可用键并转换为标准格式"""
        processed = {}

        if 'heatmap_data' in self.data:
            processed['heatmap'] = np.array(self.data['heatmap_data'], dtype=np.float32)
        else:
            raise ValueError("文件中未找到 'heatmap_data' 键")

        # 提取其他元数据
        processed['tank_shape'] = self.data.get('tank_shape', 'unknown')
        processed['scale_factor'] = self.data.get('scale_factor', 5)
        processed['total_duration'] = self.data.get('total_duration', None)
        processed['trapezoid_side'] = self.data.get('trapezoid_side', None)

        return processed

    # 属性访问方法
    @property
    def heatmap(self):
        """返回预处理后的热图数组"""
        return self._processed.get('heatmap')

    def get_processed(self):
        """返回预处理后的数据字典"""
        return self._processed

def main():
    """脚本运行入口，加载并打印热图数据信息"""
    parser = argparse.ArgumentParser(description="从 .npy 文件中提取并预处理热图数据")
    parser.add_argument('--npy_file', required=True, help='.npy 文件路径')
    args = parser.parse_args()

    loader = HeatmapLoader(args.npy_file)
    data = loader.get_processed()

    print("预处理后的数据键:")
    for k in data:
        print(f"  - {k}")

    print(f"\nHeatmap Shape: {loader.heatmap.shape}")
    print(f"Heatmap Data Type: {loader.heatmap.dtype}")
    print(f"Heatmap Min Value: {loader.heatmap.min()}")
    print(f"Heatmap Max Value: {loader.heatmap.max()}")
    print(f"Tank Shape: {data['tank_shape']}")
    print(f"Scale Factor: {data['scale_factor']}")
    print(f"Total Duration: {data['total_duration']}")

if __name__ == '__main__':
    main()