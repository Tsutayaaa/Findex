#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
beh_loader.py

该模块从 .npy 文件中提取鱼类行为数据，兼容老版本和新版本格式（忽略 'heatmap_data'），
预处理后形成标准数据结构，支持神经网络训练输入。

用法（脚本运行）：
    python beh_loader.py --npy_file path/to/data.npy

用法（模块调用）：
    from beh_loader import BehaviorLoader
    loader = BehaviorLoader("path/to/data.npy")
    print(loader.top_time)
    print(loader.speeds)
"""

import numpy as np
import argparse
import os

class BehaviorLoader:
    """
    BehaviorLoader 用于加载和预处理 .npy 文件中的鱼类行为数据，
    兼容老版本和新版本格式（忽略 'heatmap_data'），为神经网络训练提供输入。
    """
    def __init__(self, filepath):
        """初始化加载器，加载并预处理 .npy 文件"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在：{filepath}")
        self.data = np.load(filepath, allow_pickle=True).item()
        self._processed = self._preprocess()

    def _preprocess(self):
        """预处理数据，提取行为相关键并转换类型"""
        processed = {}

        # 速度相关数据
        if 'speeds_mm_s' in self.data:
            processed['speeds'] = np.array(self.data['speeds_mm_s'], dtype=np.float32)
        if 'avg_speed_mm_s' in self.data:
            processed['avg_speed'] = float(self.data['avg_speed_mm_s'])
        if 'total_displacement_mm' in self.data:
            processed['total_displacement'] = float(self.data['total_displacement_mm'])

        # 顶部行为数据
        if 'top_time' in self.data:
            processed['top_time'] = float(self.data['top_time'])
        if 'top_times' in self.data:
            processed['top_times'] = np.array(self.data['top_times'], dtype=np.float32)
        if 'top_frequency' in self.data:
            processed['top_frequency'] = int(self.data['top_frequency'])

        # 冻结行为数据
        if 'freeze_time' in self.data:
            processed['freeze_time'] = float(self.data['freeze_time'])
        if 'freeze_times' in self.data:
            processed['freeze_times'] = np.array(self.data['freeze_times'], dtype=np.float32)
        if 'freeze_frequency' in self.data:
            processed['freeze_frequency'] = int(self.data['freeze_frequency'])

        # 鱼缸配置信息
        for key in ['tank_shape', 'trapezoid_side', 'scale_factor']:
            if key in self.data:
                processed[key] = self.data[key]

        return processed

    # 属性访问方法
    @property
    def speeds(self):
        return self._processed.get('speeds')

    @property
    def avg_speed(self):
        return self._processed.get('avg_speed')

    @property
    def total_displacement(self):
        return self._processed.get('total_displacement')

    @property
    def top_time(self):
        return self._processed.get('top_time')

    @property
    def top_times(self):
        return self._processed.get('top_times')

    @property
    def top_frequency(self):
        return self._processed.get('top_frequency')

    @property
    def freeze_time(self):
        return self._processed.get('freeze_time')

    @property
    def freeze_times(self):
        return self._processed.get('freeze_times')

    @property
    def freeze_frequency(self):
        return self._processed.get('freeze_frequency')

    @property
    def tank_info(self):
        keys = ['tank_shape', 'scale_factor', 'trapezoid_side']
        return {k: self._processed.get(k) for k in keys if k in self._processed}

    def get_processed(self):
        """返回预处理后的数据字典"""
        return self._processed

def main():
    """脚本运行入口，加载并打印行为数据"""
    parser = argparse.ArgumentParser(description="从 .npy 文件中提取并预处理鱼类行为数据")
    parser.add_argument('--npy_file', required=True, help='.npy 文件路径')
    args = parser.parse_args()

    loader = BehaviorLoader(args.npy_file)
    data = loader.get_processed()

    print("预处理后的数据键:")
    for k in data:
        print(f"  - {k}")

    # 按照新版本 .npy 键顺序打印
    print("-" * 40)
    print(f"Tank Shape: {loader.tank_info.get('tank_shape')}")
    print(f"Trapezoid Side: {loader.tank_info.get('trapezoid_side')}")
    print(f"Scale Factor: {loader.tank_info.get('scale_factor')}")
    print("-" * 40)
    print(f"Total Displacement: {loader.total_displacement if loader.total_displacement is not None else 'None'}")
    print(f"Average Speed: {loader.avg_speed if loader.avg_speed is not None else 'None'}")
    print(f"Speeds array shape: {loader.speeds.shape if loader.speeds is not None else 'None'}")
    print(f"Top Time: {loader.top_time}")
    print(f"Top Times array shape: {loader.top_times.shape if loader.top_times is not None else 'None'}")
    print(f"Top Frequency: {loader.top_frequency if loader.top_frequency is not None else 'None'}")
    print(f"Freeze Time: {loader.freeze_time}")
    print(f"Freeze Times array shape: {loader.freeze_times.shape if loader.freeze_times is not None else 'None'}")
    print(f"Freeze Frequency: {loader.freeze_frequency if loader.freeze_frequency is not None else 'None'}")
    print("-" * 40)

if __name__ == '__main__':
    main()