#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Findex_Heatmap.py

从样本文件夹或母文件夹（GroupName_Index 子目录结构）读取 .npy 文件中的 heatmap_data，
按组合并相同类型鱼缸的热图，生成平滑热图，保存为 <group_name> (n=x).png。
热图标准化为每秒停留概率，矩形热图添加顶部判定线。

预设：
- Rectangle: width=200mm, height=200mm, scale_factor=5
- Trapezoid: top_width=270mm, bottom_width=220mm, height=145mm, scale_factor=5

用法：
    python Findex_Heatmap.py                # 打开 GUI
    python Findex_Heatmap.py --folders <path1> <path2> ... --output_dir output_folder [--fuzzy] [--kernel_size 15] [--heatmap_alpha 0.8]
"""
import os
import glob
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
from loader import HeatmapLoader, BehaviorLoader
from datetime import datetime
import logging  # 引入 logging 模块

try:
    from fuzzywuzzy import process, fuzz
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 鱼缸预设
TANK_PRESETS = {
    "rectangle": {"real_width_mm": 200, "real_height_mm": 200, "scale_factor": 5},
    "trapezoid": {"real_width_top_mm": 270, "real_width_bottom_mm": 220, "real_height_mm": 145, "scale_factor": 5}
}

# 语言字典（保持不变）
LANGUAGES = {
    '简中': {
        'title': 'Findex_Heatmap_1.0.1',
        'folder_label': '请选择样本文件夹（支持母文件夹，显示子文件夹）：',
        'add_button': '添加文件夹',
        'remove_button': '删除选中',
        'fuzzy_check': '启用自动模糊匹配',
        'fuzzy_tip': '提示：模糊匹配需要安装 fuzzywuzzy',
        'fuzzy_info': '模糊检索文件夹的组命名，将名称相近的样本\n自动分为一组（如 "Caffiene" 和 "caffeine"）',
        'kernel_label': '平滑核大小:',
        'alpha_label': '热图透明度:',
        'output_label': '输出文件夹：',
        'browse_button': '浏览',
        'generate_button': '生成合并热图',
        'no_folders': '警告',
        'no_folders_msg': '请先添加文件夹',
        'no_output': '警告',
        'no_output_msg': '请选择输出文件夹',
        'no_fuzzy': '警告',
        'no_fuzzy_msg': '模糊匹配需要安装 fuzzywuzzy',
        'no_data': '提示',
        'no_data_msg': '未找到有效 heatmap_data 或合并失败',
        'success': '✅ 已保存 '
    },
    'EN': {
        'title': 'Findex_Heatmap_1.0.1',
        'folder_label': 'Please select sample folders (supports parent folders with subfolders):',
        'add_button': 'Add Folder',
        'remove_button': 'Remove Selected',
        'fuzzy_check': 'Enable Fuzzy Matching',
        'fuzzy_tip': 'Note: Fuzzy matching requires fuzzywuzzy',
        'fuzzy_info': 'Fuzzy search the group naming of the folder,'
                      '\n and automatically group the samples with similar'
                      '\n names into one group. (e.g., "Caffiene" and "caffeine")',
        'kernel_label': 'Kernel Size:',
        'alpha_label': 'Heatmap Alpha:',
        'output_label': 'Output Folder:',
        'browse_button': 'Browse',
        'generate_button': 'Generate Merged Heatmaps',
        'no_folders': 'Warning',
        'no_folders_msg': 'Please add folders first',
        'no_output': 'Warning',
        'no_output_msg': 'Please select an output folder',
        'no_fuzzy': 'Warning',
        'no_fuzzy_msg': 'Fuzzy matching requires fuzzywuzzy',
        'no_data': 'Info',
        'no_data_msg': 'No valid heatmap_data found or merging failed',
        'success': '✅ Saved '
    }
}

# ToolTip 类（保持不变）
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height()
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left', background="#ffffe0", relief='solid', borderwidth=1)
        label.pack()

    def hide_tip(self, event):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

def load_heatmap_data(folder):
    """从文件夹加载 heatmap_data 和其他元数据，遍历所有 .npy 文件以确保兼容性"""
    npy_files = glob.glob(os.path.join(folder, '*.npy'))
    if not npy_files:
        logging.info(f"No .npy files found in {folder}")
        return None, None, None, None, None

    heatmap = None
    tank_shape = 'unknown'
    scale_factor = 5  # 默认值
    total_duration = None
    folder_name = os.path.basename(os.path.normpath(folder))

    # 遍历所有 .npy 文件，尝试加载热图和元数据
    for npy_file in npy_files:
        try:
            # 尝试用 HeatmapLoader 加载
            heatmap_loader = HeatmapLoader(npy_file)
            heatmap_data = np.load(npy_file, allow_pickle=True)
            logging.info(f"Keys in {npy_file}: {list(heatmap_data.item().keys()) if isinstance(heatmap_data, np.ndarray) and heatmap_data.ndim == 0 else 'Not a dict'}")
            if heatmap_loader.heatmap is not None and np.any(heatmap_loader.heatmap):
                heatmap = heatmap_loader.heatmap
                # 如果是新版本，热图文件中包含元数据
                data = heatmap_loader.get_processed()
                logging.info(f"Processed data from HeatmapLoader {npy_file}: {data}")
                if 'tank_shape' in data:
                    tank_shape = data.get('tank_shape', 'unknown')
                    scale_factor = data.get('scale_factor', TANK_PRESETS.get(tank_shape, {}).get('scale_factor', 5))
                    total_duration = data.get('total_duration', None)
                    logging.info(f"Loaded heatmap and metadata from {npy_file}: shape={heatmap.shape}, tank_shape={tank_shape}")
                    return heatmap, tank_shape, scale_factor, folder_name, total_duration
                # 如果没有元数据，继续寻找

            # 尝试用 BehaviorLoader 加载元数据（老版本或分离存储）
            beh_loader = BehaviorLoader(npy_file)
            beh_data = beh_loader.get_processed()
            logging.info(f"Processed data from BehaviorLoader {npy_file}: {beh_data}")
            if beh_data:
                tank_shape = beh_data.get('tank_shape', 'unknown')
                scale_factor = beh_data.get('scale_factor', TANK_PRESETS.get(tank_shape, {}).get('scale_factor', 5))
                total_duration = beh_data.get('total_duration', None)
                logging.info(f"Loaded metadata from {npy_file}: tank_shape={tank_shape}")

        except Exception as e:
            logging.error(f"Error processing {npy_file}: {e}")
            continue

    # 如果找到元数据但缺少热图，再次遍历寻找热图
    if tank_shape != 'unknown' and heatmap is None:
        for npy_file in npy_files:
            try:
                heatmap_loader = HeatmapLoader(npy_file)
                if heatmap_loader.heatmap is not None and np.any(heatmap_loader.heatmap):
                    heatmap = heatmap_loader.heatmap
                    logging.info(f"Loaded heatmap from {npy_file}: shape={heatmap.shape}")
                    return heatmap, tank_shape, scale_factor, folder_name, total_duration
            except Exception as e:
                logging.error(f"Error loading heatmap from {npy_file}: {e}")
                continue

    # 如果仍未找到有效热图
    if heatmap is None or not np.any(heatmap):
        logging.info(f"No valid heatmap data found in {folder}")
        return None, None, None, None, None

    return heatmap, tank_shape, scale_factor, folder_name, total_duration

def resolve_folders(paths):
    """解析文件夹路径，找到包含 .npy 文件的子目录"""
    valid = []
    for p in paths:
        if not os.path.isdir(p):
            continue
        if glob.glob(os.path.join(p, '*.npy')):
            valid.append(p)
            continue
        for sub in os.listdir(p):
            subp = os.path.join(p, sub)
            if os.path.isdir(subp) and glob.glob(os.path.join(subp, '*.npy')):
                valid.append(subp)
    return sorted(set(valid))

def resize_heatmap(heatmap, current_scale, target_scale, tank_shape):
    """根据 scale_factor 调整热图大小"""
    if current_scale == target_scale:
        return heatmap

    preset = TANK_PRESETS.get(tank_shape)
    if not preset:
        raise ValueError(f"未知的鱼缸类型: {tank_shape}")

    if tank_shape == "rectangle":
        target_width = int(preset["real_width_mm"] / target_scale)
        target_height = int(preset["real_height_mm"] / target_scale)
    else:  # trapezoid
        target_width = int(max(preset["real_width_top_mm"], preset["real_width_bottom_mm"]) / target_scale)
        target_height = int(preset["real_height_mm"] / target_scale)

    scale_ratio = current_scale / target_scale
    if scale_ratio >= 1:
        resized = np.zeros((target_height, target_width), dtype=np.float32)
        h, w = min(int(heatmap.shape[0] * scale_ratio), target_height), min(int(heatmap.shape[1] * scale_ratio), target_width)
        resized[:h, :w] = heatmap[:h, :w]
    else:
        resized = cv2.resize(heatmap, (target_width, target_height), interpolation=cv2.INTER_NEAREST)
    return resized

def normalize_heatmap(heatmap, tank_shape):
    """梯形鱼缸填充黑色"""
    preset = TANK_PRESETS.get(tank_shape)
    if tank_shape == "trapezoid":
        expected_width = int(max(preset["real_width_top_mm"], preset["real_width_bottom_mm"]) / TANK_PRESETS[tank_shape]["scale_factor"])
        expected_height = int(preset["real_height_mm"] / TANK_PRESETS[tank_shape]["scale_factor"])
        mask = np.ones_like(heatmap, dtype=bool)
        top_width = int(preset["real_width_top_mm"] / TANK_PRESETS[tank_shape]["scale_factor"])
        bottom_width = int(preset["real_width_bottom_mm"] / TANK_PRESETS[tank_shape]["scale_factor"])
        for y in range(expected_height):
            width_at_y = int(custom_map(y, 0, expected_height - 1, top_width, bottom_width))
            offset = (expected_width - width_at_y) // 2
            mask[y, offset:offset + width_at_y] = False
        heatmap[mask] = 0
    return heatmap

def custom_map(value, in_min, in_max, out_min, out_max):
    """线性映射函数"""
    return out_min + (value - in_min) * (out_max - out_min) / (in_max - in_min)

def build_group_map(folders):
    """自动构建组名映射表"""
    raw_groups = [os.path.basename(os.path.normpath(f)).split('_')[0].lower() for f in folders]
    unique_groups = sorted(set(raw_groups))
    group_map = {}
    matched = set()
    for group in unique_groups:
        if group in matched:
            continue
        similar = [g for g in unique_groups if g not in matched and fuzz.token_sort_ratio(group, g) > 85]
        if similar:
            standard = max(similar, key=lambda x: raw_groups.count(x))
            for s in similar:
                group_map[s] = standard
                matched.add(s)
        else:
            group_map[group] = group
    return group_map

def merge_heatmaps(folders, output_dir, fuzzy_match=False, kernel_size=15, heatmap_alpha=0.8):
    """按组合并热图并保存"""
    heatmaps = []
    tank_shapes = []
    scale_factors = []
    folder_names = []
    total_durations = []

    sub_folders = resolve_folders(folders)
    for folder in sub_folders:
        heatmap, tank_shape, scale_factor, folder_name, total_duration = load_heatmap_data(folder)
        if heatmap is not None and np.any(heatmap):  # 确保热图非空
            heatmaps.append(heatmap)
            tank_shapes.append(tank_shape)
            scale_factors.append(scale_factor)
            folder_names.append(folder_name)
            total_durations.append(total_duration)

    if not heatmaps:
        logging.info("未找到有效的 heatmap_data")
        return []

    # 模糊匹配组名
    group_map = build_group_map(sub_folders) if fuzzy_match and FUZZY_AVAILABLE else None
    groups = {}
    for i, folder_name in enumerate(folder_names):
        group_name = extract_group(folder_name, fuzzy_match, group_map)
        if group_name not in groups:
            groups[group_name] = {'heatmaps': [], 'tank_shapes': [], 'scale_factors': [], 'total_durations': []}
        groups[group_name]['heatmaps'].append(heatmaps[i])
        groups[group_name]['tank_shapes'].append(tank_shapes[i])
        groups[group_name]['scale_factors'].append(scale_factors[i])
        groups[group_name]['total_durations'].append(total_durations[i])

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    results = []

    for group_name, data in groups.items():
        heatmaps = data['heatmaps']
        tank_shapes = data['tank_shapes']
        scale_factors = data['scale_factors']
        total_durations = data['total_durations']

        unique_shapes = set(tank_shapes)
        if len(unique_shapes) > 1:
            target_shape = tank_shapes[0]
            heatmaps = [h for h, t in zip(heatmaps, tank_shapes) if t == target_shape]
            scale_factors = [s for s, t in zip(scale_factors, tank_shapes) if t == target_shape]
            total_durations = [d for d, t in zip(total_durations, tank_shapes) if t == target_shape]
        else:
            target_shape = tank_shapes[0]

        # 统一 scale_factor
        target_scale = min(scale_factors)
        resized_heatmaps = [resize_heatmap(h, s, target_scale, target_shape) for h, s in zip(heatmaps, scale_factors)]
        normalized_heatmaps = [normalize_heatmap(h, target_shape) for h in resized_heatmaps]
        merged_heatmap = np.mean(normalized_heatmaps, axis=0)

        # 平滑热图
        kernel_size = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
        heatmap_smoothed = cv2.GaussianBlur(merged_heatmap, (kernel_size, kernel_size), 0)

        # 标准化为每秒停留概率
        avg_total_duration = np.mean([d for d in total_durations if d is not None]) if any(
            d is not None for d in total_durations) else 1.0
        heatmap_prob = heatmap_smoothed / avg_total_duration if avg_total_duration > 0 else heatmap_smoothed

        # 可视化
        plt.figure(figsize=(10, 8))
        norm = Normalize(vmin=heatmap_prob.min(), vmax=heatmap_prob.max())
        im = plt.imshow(heatmap_prob, cmap='jet', norm=norm, alpha=heatmap_alpha, zorder=1)

        # 添加矩形中间判定线，确保线条不超出热图
        if target_shape == "rectangle":
            top_line_y = heatmap_prob.shape[0] // 2  # 中间位置
            heatmap_width = heatmap_prob.shape[1]    # 热图宽度
            plt.plot([0, heatmap_width - 1], [top_line_y, top_line_y], color='red', linestyle='--', linewidth=2,
                     label='Center Line', zorder=50)

        # 添加比例尺
        cbar = plt.colorbar(im)
        cbar.set_label('Stay Probability (per second)', rotation=270, labelpad=15)
        cbar.set_ticks(np.linspace(heatmap_prob.min(), heatmap_prob.max(), 5))

        # 添加组名和样本数
        sample_size = len(heatmaps)
        plt.text(heatmap_prob.shape[1] - 10, heatmap_prob.shape[0] - 10,
                 f"{group_name} (n={sample_size})",
                 color='white', fontsize=12, ha='right', va='bottom',
                 bbox=dict(facecolor='black', alpha=0.5), zorder=100)

        # 显示图例（可选）
        if target_shape == "rectangle":
            plt.legend(loc='upper right')

        plt.axis('off')
        output_file = os.path.join(output_dir, f"{group_name} (n={sample_size}).png")
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        results.append(output_file)

    return results

def extract_group(folder_name: str, fuzzy_match=False, group_map=None) -> str:
    base_group = folder_name.split('_')[0].lower()
    if fuzzy_match and FUZZY_AVAILABLE and group_map:
        return group_map.get(base_group, base_group)
    return base_group

class HeatmapGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.language = 'EN'  # 默认英文
        self.texts = LANGUAGES[self.language]
        self.title(self.texts['title'])
        self.geometry('600x500')
        self.folders = []
        self.fuzzy_match = tk.BooleanVar(value=False)
        self.kernel_size = tk.IntVar(value=61)
        self.heatmap_alpha = tk.DoubleVar(value=0.8)
        self.build_ui()

    def build_ui(self):
        # 第一行：文件夹标签和语言选择
        top_frame = tk.Frame(self)
        top_frame.pack(fill='x', padx=10, pady=5)
        self.folder_label = tk.Label(top_frame, text=self.texts['folder_label'])
        self.folder_label.pack(side='left', anchor='w')
        lang_frame = tk.Frame(top_frame)
        lang_frame.pack(side='right')
        tk.Label(lang_frame, text='Language:').pack(side='left')
        self.lang_var = tk.StringVar(value=self.language)
        self.lang_menu = ttk.Combobox(lang_frame, textvariable=self.lang_var, values=['简中', 'EN'], state='readonly', width=5)
        self.lang_menu.pack(side='left')
        self.lang_menu.bind('<<ComboboxSelected>>', self.switch_language)

        self.lb = tk.Listbox(self, selectmode=tk.EXTENDED)
        self.lb.pack(fill='both', expand=True, padx=10)

        frame = tk.Frame(self)
        frame.pack(fill='x', padx=10, pady=5)
        self.add_button = tk.Button(frame, text=self.texts['add_button'], command=self.add_folder)
        self.add_button.pack(side='left')
        self.remove_button = tk.Button(frame, text=self.texts['remove_button'], command=self.remove_selected)
        self.remove_button.pack(side='left', padx=5)
        self.fuzzy_check = tk.Checkbutton(frame, text=self.texts['fuzzy_check'], variable=self.fuzzy_match,
                                         state='disabled' if not FUZZY_AVAILABLE else 'normal')
        self.fuzzy_check.pack(side='left', padx=5)
        self.fuzzy_info = tk.Label(frame, text='ⓘ', font=('Arial', 8), fg='black')
        self.fuzzy_info.pack(side='left', padx=2)
        ToolTip(self.fuzzy_info, self.texts['fuzzy_info'])

        param_frame = tk.Frame(self)
        param_frame.pack(fill='x', padx=10, pady=5)
        self.kernel_label = tk.Label(param_frame, text=self.texts['kernel_label'])
        self.kernel_label.pack(side='left')
        tk.Entry(param_frame, textvariable=self.kernel_size, width=5).pack(side='left', padx=5)
        self.alpha_label = tk.Label(param_frame, text=self.texts['alpha_label'])
        self.alpha_label.pack(side='left')
        tk.Entry(param_frame, textvariable=self.heatmap_alpha, width=5).pack(side='left', padx=5)

        out_frame = tk.Frame(self)
        out_frame.pack(fill='x', padx=10, pady=5)
        self.output_label = tk.Label(out_frame, text=self.texts['output_label'])
        self.output_label.pack(side='left')
        self.out_entry = tk.Entry(out_frame)
        self.out_entry.pack(side='left', fill='x', expand=True, padx=5)
        self.browse_button = tk.Button(out_frame, text=self.texts['browse_button'], command=self.choose_output)
        self.browse_button.pack(side='left')

        self.generate_button = tk.Button(self, text=self.texts['generate_button'], command=self.generate)
        self.generate_button.pack(pady=10)
        self.status = tk.Label(self, text=self.texts['fuzzy_tip'] if not FUZZY_AVAILABLE else '')
        self.status.pack()

    def switch_language(self, event=None):
        """Switch language and update UI"""
        self.language = self.lang_var.get()
        self.texts = LANGUAGES[self.language]
        self.title(self.texts['title'])
        self.folder_label.config(text=self.texts['folder_label'])
        self.add_button.config(text=self.texts['add_button'])
        self.remove_button.config(text=self.texts['remove_button'])
        self.fuzzy_check.config(text=self.texts['fuzzy_check'])
        self.fuzzy_info_tip = ToolTip(self.fuzzy_info, self.texts['fuzzy_info'])  # 更新提示文本
        self.kernel_label.config(text=self.texts['kernel_label'])
        self.alpha_label.config(text=self.texts['alpha_label'])
        self.output_label.config(text=self.texts['output_label'])
        self.browse_button.config(text=self.texts['browse_button'])
        self.generate_button.config(text=self.texts['generate_button'])
        self.status.config(text=self.texts['fuzzy_tip'] if not FUZZY_AVAILABLE else '')

    def add_folder(self):
        path = filedialog.askdirectory(title='选择文件夹' if self.language == 'zh' else 'Select Folder')
        if not path:
            return
        sub_folders = resolve_folders([path])
        for folder in sub_folders:
            if folder not in self.folders:
                self.folders.append(folder)
                self.lb.insert('end', folder)

    def remove_selected(self):
        for i in reversed(self.lb.curselection()):
            self.folders.pop(i)
            self.lb.delete(i)

    def choose_output(self):
        path = filedialog.askdirectory(title='选择输出文件夹' if self.language == 'zh' else 'Select Output Folder')
        if path:
            default_subfolder = f"Heatmaps_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            full_path = os.path.join(path, default_subfolder)
            self.out_entry.delete(0, 'end')
            self.out_entry.insert(0, full_path)

    def generate(self):
        out_dir = self.out_entry.get().strip()
        if not self.folders:
            return messagebox.showwarning(self.texts['no_folders'], self.texts['no_folders_msg'])
        if not out_dir:
            return messagebox.showwarning(self.texts['no_output'], self.texts['no_output_msg'])

        fuzzy = self.fuzzy_match.get()
        if fuzzy and not FUZZY_AVAILABLE:
            return messagebox.showwarning(self.texts['no_fuzzy'], self.texts['no_fuzzy_msg'])

        kernel = self.kernel_size.get()
        heatmap_a = self.heatmap_alpha.get()

        results = merge_heatmaps(self.folders, out_dir, fuzzy_match=fuzzy,
                                 kernel_size=kernel, heatmap_alpha=heatmap_a)
        if results:
            self.status.config(text=f"{self.texts['success']}{len(results)} 张热图至: {out_dir}")
        else:
            messagebox.showinfo(self.texts['no_data'], self.texts['no_data_msg'])

def main():
    parser = argparse.ArgumentParser(description="合并热图工具")
    parser.add_argument('--folders', nargs='+', help='样本文件夹路径或母文件夹')
    parser.add_argument('--output_dir', help='输出文件夹路径（默认使用时间戳）')
    parser.add_argument('--fuzzy', action='store_true', help='启用自动模糊匹配')
    parser.add_argument('--kernel_size', type=int, default=15, help='高斯核大小')
    parser.add_argument('--heatmap_alpha', type=float, default=0.8, help='热图透明度 (0-1)')
    args = parser.parse_args()

    if args.folders:
        output_dir = args.output_dir if args.output_dir else f"Heatmaps_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if args.fuzzy and not FUZZY_AVAILABLE:
            print("错误：模糊匹配需要安装 fuzzywuzzy")
            return
        results = merge_heatmaps(args.folders, output_dir, fuzzy_match=args.fuzzy,
                                 kernel_size=args.kernel_size, heatmap_alpha=args.heatmap_alpha)
        if results:
            print(f"已保存 {len(results)} 张热图至: {output_dir}")
            for r in results:
                print(f"  - {r}")
        else:
            print("合并失败，未生成热图")
    else:
        HeatmapGUI().mainloop()

if __name__ == '__main__':
    main()