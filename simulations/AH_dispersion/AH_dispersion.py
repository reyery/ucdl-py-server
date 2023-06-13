#!/opt/local/bin/python2.7
##
## A python code to calculate AH dispersion 
##
## Due to SSL certificate problem, this script has to be run with some version of python > 2.7.6
##
## Written by He Wenhui at FRS, Finished on August 24, 2021

import gc
import time
import arcpy
from arcpy import env
from arcpy.sa import *
from arcpy.ia import *
import sys
import json
import os
# RASTER_DEM=r'C:\Users\akibdpt\Documents\UCDL\python_server\AH_dispersion_result\result_84.tif'
# RASTER_DEM_DATA=arcpy.Raster(RASTER_DEM)
CWD = os.getcwd()

RASTER_DEM = CWD + r'\simulations\AH_dispersion\result.tif'
RASTER_DEM_DATA=arcpy.Raster(RASTER_DEM)

RASTER_DEM_SVY = CWD + r'\simulations\AH_dispersion\result.tif'
RASTER_DEM_SVY_DATA=arcpy.Raster(RASTER_DEM_SVY)



def run_AH_dispersion(bounds):
    env.overwriteOutput = True

    session = str(time.time_ns())

    data_list=[]
    data_extent = str(RASTER_DEM_DATA.extent)
    data_proj = RASTER_DEM_DATA.spatialReference.exportToString()
    try:
        minmax = [10000000, 10000000, -10000000, -10000000]
        for coords in bounds:
            minmax[0] = min(minmax[0], coords[0])
            minmax[1] = min(minmax[1], coords[1])
            minmax[2] = max(minmax[2], coords[0])
            minmax[3] = max(minmax[3], coords[1])
        for i in range(len(minmax)):
            minmax[i] = str(minmax[i])

        DEM = arcpy.Clip_management(RASTER_DEM, ' '.join(minmax), "./temp_result/cut_ah_" + session + '.tif', "#", "#", "NONE")
        DEM = arcpy.Raster( "./temp_result/cut_ah_" + session + '.tif')

        data_array = arcpy.RasterToNumPyArray("./temp_result/cut_ah_" + session + '.tif', nodata_to_value=0)
        data_list = data_array.tolist()
        data_extent = str(DEM.extent)
        data_proj = DEM.spatialReference.exportToString()
    except Exception as ex:
        print('ERROR:', ex)

    if arcpy.Exists("in_memory"):
        arcpy.Delete_management("in_memory")
    arcpy.Delete_management("./temp_result/cut_ah_" + session + '.tif')
    gc.collect()
    return {
        "data": data_list,
        "extent": data_extent,
        "proj": data_proj,
        "nodata": 0
    }


def run_AH_dispersion_svy(bounds):
    return run_AH_dispersion(bounds)
