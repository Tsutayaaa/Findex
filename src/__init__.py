# src/__init__.py
__version__ = "1.0.0"
__author__ = "Shulei.He"

from loader.heat_loader import HeatmapLoader
from loader.beh_loader import BehaviorLoader
from .Findex_Data import  main as findex_data_main
from .Findex_Heatmap import main as findex_heatmap_main