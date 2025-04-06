# 🐟Findex📊

 Findex 是一款配套与zebrAI_fish的统计绘图工具。其可以读取zebrAI_fish在样本文件夹生成的.npy文件的参数，导出统计表格或者合成热图。

同时其内置的loader模块提供了适配zebrAI_fish .npy文件的调用接口，可以提供标准化的调用方法。

# 🔧功能

Findex v1.0 目前包含两个子程序：Findex_Data & Findex_Heatmap

## **Findex_Data**

用于读取zebrAI_fish所生成的behavior_data.npy文件（v1.1.0之后版本），或者data.npy文件。

软件会自动将指定目录下的所有样本文件夹按照命名进行分组，并统计npy文件中的以下内容：

| 名称 | 描述 | 版本兼容 |
| --- | --- | --- |
| Group | 实验分组名称（如：对照组、处理组） |  |
| Top Duration | 在鱼缸上层活动的总时长（秒） |  |
| Top Frequency | 进入鱼缸上层的次数 |  |
| Freeze Duration | 冻结状态的总时长（秒） |  |
| Freeze Frequency | 出现冻结行为的次数 |  |
| Latency to the Top | 首次进入鱼缸上层的潜伏期（秒） | zebrAI_fish_v1.1.0之后版本 |
| Total Displacement | 总位移距离（毫米） | zebrAI_fish_v1.1.0之后版本 |
| Average Speed | 平均移动速度（毫米/秒） | zebrAI_fish_v1.1.0之后版本 |
| Tank Shape | 鱼缸形状（如：rectangle，trapezoid） |  |
| Folder Name | 原始数据文件夹名称 |  |

生成.excel或.csv格式文件，并进行简单的排版和均值计算。

## **Findex_Heatmap**

用于读取zebrAI_fish所生成的heatmap_data.npy文件（v1.1.0之后版本），或者data.npy文件。

软件会自动将指定目录下的所有样本文件夹按照命名进行分组，将相同组的热图进行合并显示。

![c_(n6)](https://github.com/user-attachments/assets/a1484bf1-4d8e-451d-b7c1-34dde4e08c7c)


## Loader模块

安装完整项目代码可以使用其中./src/loader目录下的`beh_loader.py` 和 `heat_loader.py` 作为脚本或者模块使用，用来访问.npy文件中的所有内容。

```bash
#用法（脚本运行）：
python heat_loader.py --npy_file path/to/heatmap_data.npy
```

```python
#用法（模块调用）：
from heat_loader import HeatmapLoader
loader = HeatmapLoader("path/to/heatmap_data.npy")
print(loader.heatmap.shape)
```

# 📦安装与部署

## 软件安装（客户端）

Findex 支持 **Windows** 与 **macOS** 平台，分别提供独立的可执行版本，用户无需安装 Python 环境即可使用。

### 下载地址

- **Windows 版本**：
    
    下载地址：`https://github.com/Tsutayaaa/Findex/releases/download/v1.0.1-update/Findex_v1.0.1_windows.zip`
    
- **macOS 版本**：
    
    下载地址：`https://github.com/Tsutayaaa/Findex/releases/download/v1.0.1-update/Findex_v1.0.1_macos.zip`
    

### 解压内容说明

每个压缩包中包含两个独立子程序：

- `Findex_Data`：用于行为统计分析
- `Findex_Heatmap`：用于热图可视化

可根据需要单独运行其中任意程序。

### 安装与使用指南

1. 下载并解压对应操作系统的 `.zip` 文件；
2. **Windows 用户**：双击运行 `Findex_Data.exe` 或 `Findex_Heatmap.exe`；
3. **macOS 用户**：双击运行 `Findex_Data.app` 或 `Findex_Heatmap.app`；
    - 若遇到安全提示，请在“系统设置 → 隐私与安全性”中允许打开应用。

## 项目部署（开发者）

### **克隆项目**

```bash
git clone https://github.com/Tsutayaaa/Findex.git
cd Findex
```

### **创建并激活虚拟环境**

建议使用 Anaconda / Miniconda

```bash
conda create -n findex python=3.11
conda activate findex
```

或者使用 venv（标准 Python）：

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### **安装依赖**

```bash
pip install -r requirements.txt
```

# 🦾软件使用方法

## Findex_Data

<img width="712" alt="image" src="https://github.com/user-attachments/assets/b990a0a2-4dac-4365-aa67-b36f7dce627c" />

- 点击’添加文件夹‘添加样本文件，支持单独添加样本文件夹（eg.Control_001），或者直接添加包含多个样本文件夹的母文件夹。
- 点击’输出路径‘后的’浏览‘选择输出目录以及导出表格的格式（excel或csv）。
- 点击’生成统计表‘，下方提示出现证明导出成功。

## Findex_Heatmap

<img width="712" alt="image 1" src="https://github.com/user-attachments/assets/b7b757f3-7d45-4410-afdb-ca8069c171e2" />

- 点击’添加文件夹‘添加样本文件，支持单独添加样本文件夹（eg.Control_001），或者直接添加包含多个样本文件夹的母文件夹。
- 软件提供‘平滑核大小’和’热图透明度‘两个热图调整指标。
- 点击’输出路径‘后的’浏览‘选择输出目录，软件会在该路径下生成一个包含所有热图的文件夹。
- 点击’生成合并热图‘，下方提示出现证明导出成功。

<img width="981" alt="image 2" src="https://github.com/user-attachments/assets/b9a3c0ee-eebf-4752-aad6-1a04af2bb5d2" />


## 自动模糊匹配

Findex_Data和Findex_Heatmap都提供了样本名自动模糊匹配功能（源码需要安装`fuzzywuzzy`）

<img width="712" alt="截屏2025-04-06_20 46 41" src="https://github.com/user-attachments/assets/12baa940-0f04-4e12-a3c9-b874bf4cdfab" />

> 例如：该组样本中caffeine存在“caffiene”拼写错误和“Caffeine”大小写不一致情况。
> 

开启自动模糊匹配后软件会自动识别相似组名归类为数量最多的名称。

<img width="1042" alt="image 3" src="https://github.com/user-attachments/assets/218d9c6a-35ff-45e5-b2d7-8dd5a744fa55" />


# 🙌贡献

Findex 是一个开源项目，欢迎任何形式的贡献！

你可以通过以下方式参与：

- 提交 Issue 反馈 bug 或建议
- Fork 并提交 Pull Request 增强功能或优化代码
- 改进文档与本地化内容

我们鼓励社区参与，共同完善本项目！

# 📄许可证

本项目采用 [MIT License](https://opensource.org/licenses/MIT) 开源协议。

你可以自由地使用、修改和分发该软件，但请保留原始许可声明。

# 🧾致谢

该软件由 **Shulei He** 开发，隶属于 **西交利物浦大学理学院**

(School of Science, Xi’an Jiaotong-Liverpool University, [www.xjtlu.edu.cn](https://www.xjtlu.edu.cn/))。

本项目托管于 GitHub：https://github.com/Tsutayaaa/Findex

如果你在科研或实验中使用了本软件，**请在相关出版物中引用本项目 GitHub 地址以示致谢**。

可以按如下方式致谢：
> This study made use of the Findex software developed by Shulei He (School of Science, Xi’an Jiaotong-Liverpool University), available at [https://github.com/Tsutayaaa/Findex](https://github.com/Tsutayaaa/Findex).
