#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Findex_Data.py

Batch process one or more result folders or a parent folder (GroupName_Index structure),
extract behavioral metrics from .npy files in subdirectories, and generate an Excel/CSV summary table.

Output columns: Group, Top Duration, Top Frequency, Freeze Duration, Freeze Frequency,
               Latency to the Top, Total Displacement, Average Speed, Tank Shape, Folder Name

Features: Sort by Group with group means (including sample size), add blank rows between groups,
          optional fuzzy matching for group names. Supports English/Chinese UI switching.

Dependencies: pandas, tkinter, beh_loader, fuzzywuzzy (optional for fuzzy matching)

Usage:
    python Findex_Data.py                # Open GUI
    python Findex_Data.py --folders <paths> --output summary.xlsx [--fuzzy]
"""
import os
import glob
import argparse
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from loader import BehaviorLoader

try:
    from fuzzywuzzy import process, fuzz
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False

# 语言字典
LANGUAGES = {
    '简中': {
        'title': 'Findex_Data_1.0.1',
        'folder_label': '请选择文件夹（支持主文件夹或子文件夹）：',
        'add_button': '添加文件夹',
        'remove_button': '删除选中',
        'fuzzy_check': '启用自动模糊匹配',
        'fuzzy_tip': '提示：模糊匹配需要安装 fuzzywuzzy',
        'fuzzy_info': '模糊检索文件夹的组命名，将名称相近的样本\n自动分为一组（如 "Caffiene" 和 "caffeine"）',
        'output_label': '输出路径：',
        'browse_button': '浏览',
        'generate_button': '生成统计表',
        'no_folders': '警告',
        'no_folders_msg': '请先添加文件夹',
        'no_output': '警告',
        'no_output_msg': '请选择输出路径',
        'no_fuzzy': '警告',
        'no_fuzzy_msg': '模糊匹配需要安装 fuzzywuzzy',
        'no_data': '提示',
        'no_data_msg': '未找到有效 .npy 文件',
        'success': '✅ 已保存: ',
        'error': '错误'
    },
    'EN': {
        'title': 'Findex_Data_1.0.1',
        'folder_label': 'Please select folders (supports parent or subfolders):',
        'add_button': 'Add Folder',
        'remove_button': 'Remove Selected',
        'fuzzy_check': 'Enable Fuzzy Matching',
        'fuzzy_tip': 'Note: Fuzzy matching requires fuzzywuzzy',
        'fuzzy_info': 'Fuzzy search the group naming of the folder,'
                      '\n and automatically group the samples with similar'
                      '\n names into one group. (e.g., "Caffiene" and "caffeine")',
        'output_label': 'Output Path:',
        'browse_button': 'Browse',
        'generate_button': 'Generate Stats Table',
        'no_folders': 'Warning',
        'no_folders_msg': 'Please add folders first',
        'no_output': 'Warning',
        'no_output_msg': 'Please select an output path',
        'no_fuzzy': 'Warning',
        'no_fuzzy_msg': 'Fuzzy matching requires fuzzywuzzy',
        'no_data': 'Info',
        'no_data_msg': 'No valid .npy files found',
        'success': '✅ Saved: ',
        'error': 'Error'
    }
}

# ToolTip 类
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

def extract_group(folder_name: str, fuzzy_match=False, group_map=None) -> str:
    """Extract Group name from folder name, case-insensitive, with optional fuzzy matching"""
    base_group = folder_name.split('_')[0].lower()
    if fuzzy_match and FUZZY_AVAILABLE and group_map:
        return group_map.get(base_group, base_group)
    return base_group

def build_group_map(folders):
    """Build a group name mapping from folder names, merging similar spellings"""
    raw_groups = [os.path.basename(os.path.normpath(f)).split('_')[0].lower() for f in folders]
    unique_groups = sorted(set(raw_groups))

    if not unique_groups:
        return {}

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

def resolve_folders(paths):
    """Resolve folder paths to find subdirectories containing .npy files"""
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

def collect_stats(folders, fuzzy_match=False):
    """Collect stats from folders, sort by Group, add group means and blank rows"""
    group_map = build_group_map(folders) if fuzzy_match and FUZZY_AVAILABLE else None
    records = []
    for folder in folders:
        base = os.path.basename(os.path.normpath(folder))
        group = extract_group(base, fuzzy_match, group_map)
        npy_files = glob.glob(os.path.join(folder, '*.npy'))
        if not npy_files:
            continue
        loader = BehaviorLoader(npy_files[0])
        data = loader.get_processed()

        first_top_time = loader.top_times[0][0] if loader.top_times is not None and len(loader.top_times) > 0 else None

        records.append({
            'Group': group,
            'Top Duration': loader.top_time or 0.0,
            'Top Frequency': data.get('top_frequency', 0),
            'Freeze Duration': loader.freeze_time or 0.0,
            'Freeze Frequency': data.get('freeze_frequency', 0) or len(data.get('freeze_times', [])),
            'Latency to the Top': first_top_time,
            'Total Displacement': loader.total_displacement if loader.total_displacement is not None else 0.0,
            'Average Speed': loader.avg_speed if loader.avg_speed is not None else 0.0,
            'Tank Shape': loader.tank_info.get('tank_shape', 'Unknown'),
            'Folder Name': base
        })

    df = pd.DataFrame(records)
    if df.empty:
        return df

    df = df.sort_values('Group')

    numeric_cols = ['Top Duration', 'Top Frequency', 'Freeze Duration', 'Freeze Frequency',
                    'Latency to the Top', 'Total Displacement', 'Average Speed']
    grouped = df.groupby('Group')

    final_df = pd.DataFrame()
    for group, group_df in grouped:
        final_df = pd.concat([final_df, group_df], ignore_index=True)

        sample_size = len(group_df)
        mean_row = {'Group': f'Mean (n={sample_size})'}
        for col in numeric_cols:
            mean_row[col] = group_df[col].mean() if group_df[col].notna().any() else 0.0
        mean_row['Tank Shape'] = ''
        mean_row['Folder Name'] = ''

        final_df = pd.concat([final_df, pd.DataFrame([mean_row])], ignore_index=True)
        final_df = pd.concat([final_df, pd.DataFrame([{}])], ignore_index=True)

    return final_df

class StatsGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.language = 'EN'  # 默认英文
        self.texts = LANGUAGES[self.language]
        self.title(self.texts['title'])
        self.geometry('600x450')
        self.folders = []
        self.fuzzy_match = tk.BooleanVar(value=False)
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
        self.output_label.config(text=self.texts['output_label'])
        self.browse_button.config(text=self.texts['browse_button'])
        self.generate_button.config(text=self.texts['generate_button'])
        self.status.config(text=self.texts['fuzzy_tip'] if not FUZZY_AVAILABLE else '')

    def add_folder(self):
        path = filedialog.askdirectory(title='选择文件夹' if self.language == 'zh' else 'Select Folder')
        if not path:
            return
        for folder in resolve_folders([path]):
            if folder not in self.folders:
                self.folders.append(folder)
                self.lb.insert('end', folder)

    def remove_selected(self):
        for i in reversed(self.lb.curselection()):
            self.folders.pop(i)
            self.lb.delete(i)

    def choose_output(self):
        path = filedialog.asksaveasfilename(defaultextension='.xlsx',
                                           filetypes=[('Excel', '*.xlsx'), ('CSV', '*.csv')],
                                           title='选择输出路径' if self.language == 'zh' else 'Select Output Path')
        if path:
            self.out_entry.delete(0, 'end')
            self.out_entry.insert(0, path)

    def generate(self):
        out = self.out_entry.get().strip()
        if not self.folders:
            return messagebox.showwarning(self.texts['no_folders'], self.texts['no_folders_msg'])
        if not out:
            return messagebox.showwarning(self.texts['no_output'], self.texts['no_output_msg'])

        fuzzy = self.fuzzy_match.get()
        if fuzzy and not FUZZY_AVAILABLE:
            return messagebox.showwarning(self.texts['no_fuzzy'], self.texts['no_fuzzy_msg'])

        df = collect_stats(self.folders, fuzzy_match=fuzzy)

        if df.empty:
            return messagebox.showinfo(self.texts['no_data'], self.texts['no_data_msg'])
        try:
            if out.lower().endswith('.xlsx'):
                writer = pd.ExcelWriter(out, engine='xlsxwriter')
                df.to_excel(writer, index=False, sheet_name='Sheet1')
                worksheet = writer.sheets['Sheet1']
                for i, col in enumerate(df.columns):
                    max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.set_column(i, i, max_len)
                writer.close()
            else:
                df.to_csv(out, index=False)
            self.status.config(text=f"{self.texts['success']}{os.path.basename(out)}")
        except Exception as e:
            messagebox.showerror(self.texts['error'], str(e))

def main():
    parser = argparse.ArgumentParser(description="Statistics aggregation tool with optional fuzzy matching")
    parser.add_argument('--folders', nargs='+', help='List of folder paths')
    parser.add_argument('--output', help='Output file path (.xlsx or .csv)')
    parser.add_argument('--fuzzy', action='store_true', help='Enable fuzzy matching')
    args = parser.parse_args()

    if args.folders and args.output:
        if args.fuzzy and not FUZZY_AVAILABLE:
            print("Error: Fuzzy matching requires fuzzywuzzy")
            return
        df = collect_stats(resolve_folders(args.folders), fuzzy_match=args.fuzzy)
        if args.output.lower().endswith('.xlsx'):
            writer = pd.ExcelWriter(args.output, engine='xlsxwriter')
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            worksheet = writer.sheets['Sheet1']
            for i, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, max_len)
            writer.close()
        else:
            df.to_csv(args.output, index=False)
        print(f'Saved to {args.output}')
    else:
        StatsGUI().mainloop()

if __name__ == '__main__':
    main()