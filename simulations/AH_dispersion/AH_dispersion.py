#!/opt/local/bin/python2.7
##
## A python code to calculate AH dispersion 
##
## Due to SSL certificate problem, this script has to be run with some version of python > 2.7.6
##
## Written by He Wenhui at FRS, Finished on August 24, 2021

import gc
import time
# import arcpy
# from arcpy import env
# from arcpy.sa import *
# from arcpy.ia import *
import sys
import json
import os

import rasterio
from rasterio.mask import mask
import shapely
from pyproj import Transformer, CRS


RASTER_DEM = os.path.join(os.path.dirname(__file__), "result.tif")
# RASTER_DEM_DATA=arcpy.Raster(RASTER_DEM)
RASTER = rasterio.open(RASTER_DEM)
PROJ_TRANSFORMER = Transformer.from_crs('EPSG:4326', 'EPSG:3414', always_xy=True)


def run_AH_dispersion(bounds):
    data_list=[]
    data_extent = None
    data_proj = str(RASTER.crs)

    try:
        minmax = [10000000, 10000000, -10000000, -10000000]
        for coords in bounds:
            minmax[0] = min(minmax[0], coords[0])
            minmax[1] = min(minmax[1], coords[1])
            minmax[2] = max(minmax[2], coords[0])
            minmax[3] = max(minmax[3], coords[1])
        mask_path = [[minmax[0], minmax[1]], [minmax[0], minmax[3]], [minmax[2], minmax[3]], [minmax[2], minmax[1]]]
        for i in range(len(mask_path)):
            mask_path[i] = PROJ_TRANSFORMER.transform(mask_path[i][0], mask_path[i][1])
        mask_pgon = shapely.geometry.Polygon(mask_path)
        [mask_result, affine_transf] = mask(RASTER, [mask_pgon], all_touched = True, crop=True)
        data_list = mask_result[0].tolist()
        ex0 = affine_transf * (0,0)
        ex1 = affine_transf * (len(data_list[0]), len(data_list))
        data_extent = ' '.join([
            str(min(ex0[0], ex1[0])), str(min(ex0[1], ex1[1])), 
            str(max(ex0[0], ex1[0])), str(max(ex0[1], ex1[1]))
        ])
    except Exception as ex:
        print('ERROR:', ex)

    return {
        "data": data_list,
        "extent": data_extent,
        "proj": data_proj,
        "nodata": 0
    }


    # env.overwriteOutput = True

    # session = str(time.time_ns())

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

    #     DEM = arcpy.Clip_management(RASTER_DEM, ' '.join(minmax), "./temp_result/cut_ah_" + session + '.tif', "#", "#", "NONE")
    #     DEM = arcpy.Raster( "./temp_result/cut_ah_" + session + '.tif')

    #     data_array = arcpy.RasterToNumPyArray("./temp_result/cut_ah_" + session + '.tif', nodata_to_value=0)
    #     data_list = data_array.tolist()
    #     data_extent = str(DEM.extent)
    #     data_proj = DEM.spatialReference.exportToString()
    # except Exception as ex:
    #     print('ERROR:', ex)

    # if arcpy.Exists("in_memory"):
    #     arcpy.Delete_management("in_memory")
    # arcpy.Delete_management("./temp_result/cut_ah_" + session + '.tif')
    # gc.collect()
    # return {
    #     "data": data_list,
    #     "extent": data_extent,
    #     "proj": data_proj,
    #     "nodata": 0
    # }

