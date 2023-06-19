# import arcpy
# from arcpy import env
# from arcpy.sa import *
# import math
# import time
# import numpy
# import gc
# import sys
# import os
# import shutil
# import xlwt
# from scipy.interpolate import interp1d
# import multiprocessing

# def cal_Site_Cover_Ratio(inRaster, resolution):
#     arcpy.CheckOutExtension("Spatial")
#     resample=Float(Con(inRaster>0,1,0))
#     outRaster=Aggregate(resample, resolution, "SUM", "EXPAND", "DATA")
#     outRaster=outRaster*1.0/(resolution * resolution)
#     arcpy.Delete_management(resample)
#     del resample
#     arcpy.CheckInExtension("Spatial")
#     return outRaster
#     #return resample
