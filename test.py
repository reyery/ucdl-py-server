import arcpy
from arcpy import env
from arcpy.sa import *
import math
import time
import numpy
import gc
import sys
import os
import shutil
import xlwt
from scipy.interpolate import interp1d
from simulations.util.sim_fad import cal_Frontal_Area_Density

######################################################################################################

#input parameters
#RASTER_DEM=arcpy.GetParameterAsText(0)
RASTER_DEM=r"C:/Users/akibdpt/Documents/ArcGIS/Projects/singapore_shp/singapore_tif_3e-5/Feature_sing60.TIF"
#RESOLUTION=int(arcpy.GetParameterAsText(1))
RESOLUTION=200
#Layer_depth=int(arcpy.GetParameterAsText(2))
Layer_depth=10
#Uref=float(arcpy.GetParameterAsText(3))
Uref=7.4

#output parameters
#output_path=arcpy.GetParameterAsText(4)
output_path=r"./air_pollutant_result"
#output_name=arcpy.GetParameterAsText(5)
output_name="dem_layer"
                        
#initial parameters
MAXHEIGHT=Layer_depth+1 #for FAD calculation
env.workspace=output_path
arcpy.env.overwriteOutput = True

parameters_folder=output_path+"/parameters_folder/"
results_folder=output_path+"/results_folder/"
if not os.path.exists(parameters_folder):os.makedirs(parameters_folder)
env.scratchWorkspace=parameters_folder

# bounds =[
#     [
#         103.83489215028276,
#         1.2728772185991915
#     ],
#     [
#         103.8352599481466,
#         1.2764588005805422
#     ],
#     [
#         103.83936021211477,
#         1.2794684191829333
#     ],
#     [
#         103.8440598506779,
#         1.2852288978792785
#     ],
#     [
#         103.8528733754004,
#         1.279495656140739
#     ],
#     [
#         103.84803751492505,
#         1.27252314448711
#     ]
# ]

# DEM=arcpy.Raster(RASTER_DEM)
# array = arcpy.Array([arcpy.Point(*coords) for coords in bounds])
# array.append(array[0])

# pg = arcpy.Polygon(array)
# outExtractByMask = ExtractByMask(DEM, [pg])

# arcpy.management.MakeFeatureLayer([pg], 'mask_layer')

# outExtractByMask.save("./test_result/maskextract.tif")

def get_DEM_vertical_layer_i(DEM,Layer_depth,Layer_index):
    DEM_layer_i_tmp=Con(DEM-(Layer_depth*(Layer_index-1))>0,DEM-(Layer_depth*(Layer_index-1)),0)
    DEM_layer_i=Con(DEM_layer_i_tmp>Layer_depth,Layer_depth,DEM_layer_i_tmp)
    del DEM_layer_i_tmp
    return DEM_layer_i

IN_RASTER=r"C:/Users/akibdpt/Documents/ArcGIS/Projects/singapore_shp/singapore_tif_2/singapore_5km_16.TIF"
OUT_DIR=r"./temp_result/test_result"
if not os.path.exists(OUT_DIR): os.mkdir(OUT_DIR)
DEM=arcpy.Raster(IN_RASTER)
# arcpy.SplitRaster_management(IN_RASTER, raster_folder, 'temp_', 'SIZE_OF_TILE', 'TIFF', 
#                                         'SIZE_OF_TILE', tile_size=5000, units='METERS', cell_size='1')
lowerLeft = arcpy.Point(DEM.extent.XMin, DEM.extent.YMin)
print("The maximum building height is {0} m".format(DEM.maximum))
DEM_layers_number=int(math.ceil(DEM.maximum/Layer_depth))


for i in range(1,DEM_layers_number+1):
    print('processing layer', i, 'of', DEM_layers_number)
    splitted_fad_list = []
    DEM_Layer_i=get_DEM_vertical_layer_i(DEM,Layer_depth,i)
    DEM_Layer_i_fad,raster_list=cal_Frontal_Area_Density(DEM_Layer_i, RESOLUTION, lowerLeft,MAXHEIGHT)
    DEM_Layer_i_fad.save(OUT_DIR + '/fad_' + str(i) + '.tif')