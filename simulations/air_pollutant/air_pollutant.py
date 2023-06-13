#!/opt/local/bin/python2.7
##
## A python code to calculate AH dispersion 
##
## Due to SSL certificate problem, this script has to be run with some version of python > 2.7.6
##
## Written by He Wenhui at FRS, Finished on August 24, 2021

import arcpy
from arcpy import env
from arcpy.sa import *
from arcpy.ia import *
import sys
import json
import gc
import time 
import os

CWD = os.getcwd()
MAX_RASTER = 25
RASTER_DIR = CWD + '/simulations/air_pollutant/ap_results'
RASTERS = {}
for i in range(MAX_RASTER):
    RASTERS[i] = arcpy.Raster(RASTER_DIR + '/' + str(i + 1)  + '_V.tif')

def run_air_pollutant(bounds):
    env.overwriteOutput = True
    session = str(time.time_ns())
    data = {}
    data_extent = None
    data_proj = None
    minmax = [10000000, 10000000, -10000000, -10000000]
    try:
        for coords in bounds:
            minmax[0] = min(minmax[0], coords[0])
            minmax[1] = min(minmax[1], coords[1])
            minmax[2] = max(minmax[2], coords[0])
            minmax[3] = max(minmax[3], coords[1])
        for i in range(len(minmax)):
            minmax[i] = str(minmax[i])
    except Exception as ex:
        print('ERROR:', ex)
        return {}

    for i in RASTERS:
        RASTER_DEM = RASTERS[i]
        try:
            DEM = arcpy.Clip_management(RASTER_DEM, ' '.join(minmax), "./temp_result/cut_ap_" + str(i) + '_' + session + '.tif', "#", "#", "NONE")
            DEM = arcpy.Raster( "./temp_result/cut_ap_" + str(i) + '_' + session + '.tif')
            data_array = arcpy.RasterToNumPyArray("./temp_result/cut_ap_" + str(i) + '_' + session + '.tif', nodata_to_value=0)
            data[i] = data_array.tolist()
            if not data_extent or not data_proj:
                data_extent = str(DEM.extent)
                data_proj = DEM.spatialReference.exportToString()
        except Exception as ex:
            print('ERROR:', ex)
        arcpy.Delete_management("./temp_result/cut_ap_" + str(i) + '_' + session + '.tif')

    if arcpy.Exists("in_memory"):
        arcpy.Delete_management("in_memory")
    gc.collect()

    return {
        "data": data,
        "extent": data_extent,
        "proj": data_proj,
        "nodata": 0
    }


    # data_list=[]
    # data_extent = str(RASTER_DEM_DATA.extent)
    # data_proj = RASTER_DEM_DATA.spatialReference.exportToString()
    # try:
    #     minmax = [10000000, 10000000, -10000000, -10000000]
    #     for coords in bounds:
    #         minmax[0] = min(minmax[0], coords[0])
    #         minmax[1] = min(minmax[1], coords[1])
    #         minmax[2] = max(minmax[2], coords[0])
    #         minmax[3] = max(minmax[3], coords[1])
    #     for i in range(len(minmax)):
    #         minmax[i] = str(minmax[i])

    #     DEM = arcpy.Clip_management(RASTER_DEM, ' '.join(minmax), "./temp_result/cut_ap_" + str(i) + '_' + session + '.tif', "#", "#", "NONE")
    #     DEM = arcpy.Raster( "./temp_result/cut_ap_" + str(i) + '_' + session + '.tif')
    #     data_array = arcpy.RasterToNumPyArray("./temp_result/cut_ap_" + str(i) + '_' + session + '.tif', nodata_to_value=0)
    #     data_list = data_array.tolist()
    #     data_extent = str(DEM.extent)
    #     data_proj = DEM.spatialReference.exportToString()
    # except Exception as ex:
    #     print('ERROR:', ex)

    # if arcpy.Exists("in_memory"):
    #     arcpy.Delete_management("in_memory")
    # arcpy.Delete_management("./temp_result/cut_ap_" + str(i) + '_' + session + '.tif')
    # gc.collect()

    # return {
    #     "data": data_list,
    #     "extent": data_extent,
    #     "proj": data_proj,
    #     "nodata": 0
    # }

def get_ap():
    data = {}
    for i in RASTERS:
        data[i] = arcpy.RasterToNumPyArray(RASTERS[i], nodata_to_value=0).tolist()
    if arcpy.Exists("in_memory"):
        arcpy.Delete_management("in_memory")
    gc.collect()
    return {
        "data": data,
        "extent": str(RASTERS[0].extent),
        "proj": RASTERS[0].spatialReference.exportToString(),
        "nodata": 0
    }
