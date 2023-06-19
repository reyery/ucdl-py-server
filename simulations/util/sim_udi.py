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

# global pi
# pi = math.pi
# global EPSILON
# EPSILON = 0.00001
# global MAX_LAYER_NUMBER
# MAX_LAYER_NUMBER = 0
# WIND_DIRECTIONs=['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']

# WINDDIRECTION_ANGLESs=[270,247.5,225,202.5,180,157.5,135,112.5,90,67.5,45,22.5,0,337.5,315,292.5]

# #to calculate u_star
# U_star_lamda_f=[0.05037364, 0.057729945, 0.063935876, 0.06945358, 0.075428836, 0.08071492, 0.08645887, 0.09289184, 0.09955517, 0.10828367, 0.11724094, 0.12596802, 0.13676041, 0.14893006, 0.16293468, 0.17624964, 0.1895624, 0.20149805, 0.21297409, 0.22513852, 0.23661457, 0.2529098, 0.2646143, 0.2779253, 0.29927123, 0.31831923, 0.34081247, 0.359863, 0.3763891, 0.40232477, 0.43239823]
# U_star_divided_Uref=[0.097159654, 0.10717187, 0.11468071, 0.122659355, 0.12907284, 0.13501716, 0.13970931, 0.14471413, 0.15050131, 0.15534855, 0.1594132, 0.162852, 0.16550735, 0.16800556, 0.16893794, 0.1689317, 0.16673452, 0.16485097, 0.16249816, 0.15983203, 0.15747923, 0.15340272, 0.14995433, 0.1460357, 0.14211331, 0.13600108, 0.13160865, 0.12800033, 0.12517567, 0.11968617, 0.11967205]
# f=interp1d(U_star_lamda_f,U_star_divided_Uref,'linear', fill_value='extrapolate')

# # def calc_udi(DEM_Layer_i_fad, Uref, lowerLeft):
# def calc_udi(inRaster, Uref, lowerLeft):
#     inRaster = Raster(inRaster)
#     arcpy.CheckOutExtension("Spatial")   
#     inRaster_array=arcpy.RasterToNumPyArray(inRaster, nodata_to_value=0)
#     u_star_Array=numpy.where(inRaster_array>=0.4, 0.12*Uref, f(inRaster_array))
#     u_star=arcpy.NumPyArrayToRaster(u_star_Array,lowerLeft,inRaster.meanCellWidth,inRaster.meanCellHeight)
#     arcpy.DefineProjection_management(u_star, inRaster.spatialReference)
#     mass_exchange_velocity_ud=u_star/pi/math.sqrt(2)
#     arcpy.CheckInExtension("Spatial")
#     #arcpy.Delete_management(u_star)
#     del u_star,u_star_Array,inRaster_array
#     if arcpy.Exists("in_memory"):arcpy.Delete_management("in_memory")
#     gc.collect()
#     return mass_exchange_velocity_ud
