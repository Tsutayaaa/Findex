<h1 align="center">🐟Findex📊</h1>

<p align="center">
  <a href="README.md">中文</a> ｜ 
  <a href="README_en.md">English</a>
</p>

 Findex is a statistical plotting tool that comes with zebrAI_fish. It can read the parameters of the .npy file generated by zebrAI_fish in the sample folder, export statistical tables or synthesize heatmaps.

 At the same time, its built-in loader module provides a calling interface adapted to zebrAI_fish .npy files, which can provide a standardized calling method.

# 🔧 Features

 Findex v1.0 currently contains two subroutines: Findex_Data & Findex_Heatmap

## **Findex_Data**

 Used to read the behavior_data.npy file generated by zebraAI_fish (version after v1.1.0), or the data.npy file.

 The software will automatically group all sample folders in the specified directory by naming and count the following contents in the npy file:

|  Name |  Description |  Version Compatible |
| --- | --- | --- |
|  Group |  Experimental group name (e.g. control group, treatment group) |  |
|  Top Duration |  Total duration of activity in the upper layer of the tank (sec) |  |
|  Top Frequency |  Number of times entering the upper layer of the tank |  |
|  Freeze Duration |  Freeze Duration (sec) |  |
|  Freeze Frequency |  The number of times the freezing behavior occurs |  |
|  Latency to the Top |  Latency to the Top of the Fish Tank for the first time (seconds) |  Version after zebrAI_fish_v1.1.0 |
|  Total Displacement |  Total Displacement (mm) |  Version after zebrAI_fish_v1.1.0 |
|  Average Speed |  Average Speed (mm/s) |  Version after zebrAI_fish_v1.1.0 |
|  Tank Shape |  Tank Shape (e.g. rectangle, trapezoid) |  |
|  Folder Name |  Raw Data Folder Name |  |

 Generate .excel or .csv files with simple layout and mean calculation.

## **Findex_Heatmap**

 Used to read the heatmap_data.npy file generated by zebraAI_fish (version after v1.1.0), or the data.npy file.

 The software will automatically group all the sample folders in the specified directory according to naming, and merge the heatmaps of the same group for display.

![c_(n6)](https://github.com/user-attachments/assets/de608794-a9df-48b6-aa16-1782ab3bdbe7)


## Loader Module

 The complete project code can be installed using one of the . /src/loader directory to use `beh_loader.py` and `heat_loader.py` as scripts or modules to access everything in the .npy file.

```bash
#Usage (Script Execution)：
python heat_loader.py --npy_file path/to/heatmap_data.npy

```

```python
#Usage (Module Invocation)：
from heat_loader import HeatmapLoader
loader = HeatmapLoader("path/to/heatmap_data.npy")
print(loader.heatmap.shape)

```

# 📦 Installation and Deployment

## Software Installation (Client)

 Findex supports both **Windows** and **macOS** platforms with separate executable versions that can be used without installing the Python environment.

### Download
**[Findex_v1.0.1(Latest)](https://github.com/Tsutayaaa/Findex/releases/tag/v1.0.1-update)**
- **[Windows version](https://github.com/Tsutayaaa/Findex/releases/download/v1.0.1-update/Findex_v1.0.1_windows.zip)**:
    
     Download: `https://github.com/Tsutayaaa/Findex/releases/download/v1.0.1-update/Findex_v1.0.1_windows.zip`
    
- **[macOS version](https://github.com/Tsutayaaa/Findex/releases/download/v1.0.1-update/Findex_v1.0.1_macos.zip)**:
    
     Download: `https://github.com/Tsutayaaa/Findex/releases/download/v1.0.1-update/Findex_v1.0.1_macos.zip`
    

### Description of unzipped contents

 Each zip contains two separate subroutines:

- `Findex_Data`: for behavioral statistical analysis
- `Findex_Heatmap`: for heatmap visualization.

 You can run any of these programs separately as needed.

### Installation and Usage Guidelines

1.  Download and extract the `.zip` file for your operating system;
2. **Windows users**: Double-click to run `Findex_Data.exe` or `Findex_Heatmap.exe`;
3. **macOS users**: double-click to run `Findex_Data.app` or `Findex_Heatmap.app`;
    - If you encounter a security prompt, please allow the app to open in "System Settings → Privacy & Security".

## Project Deployment (Developers)

### **Cloning the project**

```bash
git clone <https://github.com/Tsutayaaa/Findex.git>
cd Findex

```

### **Create and activate a virtual environment**

 Anaconda / Miniconda is recommended.

```bash
conda create -n findex python=3.11
conda activate findex

```

 or use venv (standard Python):

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\\Scripts\\activate     # Windows

```

### **Install dependencies**

```bash
pip install -r requirements.txt

```

# 🦾 Software usage

## Findex_Data

<img width="712" alt="image" src="https://github.com/user-attachments/assets/4354dc59-ab25-41c9-b867-5c23c153494d" />

- Click `Add Folder` to add sample files, support to add sample folder individually (eg.Control_001), or directly add a parent folder which contains multiple sample folders.
- Click `Browse` after `Output Path` to select the output directory and the format of the export table (excel or csv).
- Click on `Generate Stats Table` and the prompt below will appear to prove that the export was successful.

## Findex_Heatmap

<img width="712" alt="image" src="https://github.com/user-attachments/assets/a5d9cb06-b2c1-42cc-bc52-0c219234b449" />

- Click `Add Folder` to add sample files, support to add separate sample folder (eg.Control_001), or directly add a parent folder containing multiple sample folders.
- The software provides two heatmap adjustment indicators: `Kernel Size` and `Heatmap Alhpa`.
- Click `Browse` after `Output Path` to select the output directory, the software will generate a folder containing all the heatmaps under this path.
- Click `Generate Merged Heatmaps`, the prompt below will appear to prove that the export is successful.

 <img width="981" alt="image 2" src="https://github.com/user-attachments/assets/24e3f27a-183c-4ac2-86cd-de5b5a76845e" />

## Auto Fuzzy Matching

 Findex_Data and Findex_Heatmap both provide automatic fuzzy matching of sample names (requires `fuzzywuzzy` )

<img width="712" alt="截屏2025-04-06 22 07 27" src="https://github.com/user-attachments/assets/4c819de3-df8b-4d5a-9016-8ca8308bf5c3" />

> For example: caffeine in this group of samples has "caffiene" misspelling and "Caffeine" abnormal capitalization.
> 

 When auto-fuzzy matching is enabled, the software will automatically recognize similar group names and categorize them into the most numerous ones.

 <img width="1042" alt="image 3" src="https://github.com/user-attachments/assets/901bbe5c-ca93-4756-bc9e-2329c8a43f8c" />

# 🙌 Contributions

 Findex is an open source project and welcomes contributions of any kind!

 You can participate in the following ways:

- Submit an Issue to give feedback on bugs or suggestions
- Fork and submit Pull Requests for feature enhancements or code optimizations.
- Improving documentation and localization

 We encourage the community to participate and work together to improve the project!

# 📄License

 This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

 You are free to use, modify, and distribute the software, but please retain the original license notice.

# 🧾Acknowledgments

 This software was developed by **Shulei He**, part of the **School of Science, Xi'an Liverpool University**.

 (School of Science, Xi'an Jiaotong-Liverpool University, [www.xjtlu.edu.cn)](https://www.xjtlu.edu.cn/).

 This project is hosted on GitHub: https: [//github.com/Tsutayaaa/Findex](https://github.com/Tsutayaaa/Findex)

 If you have used this software in your research or experiments, **please acknowledge this project by citing its GitHub address in relevant publications**.

 Acknowledgements can be made as follows:

> This study made use of the Findex software developed by Shulei He (School of Science, Xi'an Jiaotong-Liverpool University), available at https://github.com/Tsutayaaa/Findex.
>
