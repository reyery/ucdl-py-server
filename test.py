#!/opt/local/bin/python2.7
##
## A python code to calculate AH dispersion 
##
## Due to SSL certificate problem, this script has to be run with some version of python > 2.7.6
##
## Written by He Wenhui at FRS, Finished on August 24, 2021
# import arcpy
# from arcpy import env
# from arcpy.sa import *
# from arcpy.ia import *
import sys
import json
import gc
import time 
import os

import rasterio
from rasterio.mask import mask
import shapely
from pyproj import Transformer, CRS

from simulations.util.const import new_geojson_polygon

CWD = os.getcwd()
RASTER_DEM= CWD + r'\simulations\urban_wind\FAD_res200_with_wind_frequency.tif'
# RASTER_DEM_DATA=arcpy.Raster(RASTER_DEM)
RASTER = rasterio.open(RASTER_DEM)

wgs84 = CRS('EPSG:4326')
svy21 = CRS('EPSG:3414')
PROJ_TRANSFORMER = Transformer.from_crs('EPSG:4326', 'EPSG:3414', always_xy=True)

BOUNDS = RASTER.bounds
EXTENT = str(BOUNDS.left) + ' ' + str(BOUNDS.bottom) + ' ' + str(BOUNDS.right) + ' ' + str(BOUNDS.top)


def run_urban_wind(bounds):
    # env.overwriteOutput = True

    print('-------------------------------------------')
    print('extent', EXTENT)
    print('proj', RASTER.crs)

    print('===========================================')
    data_list=[]
    data_extent, data_proj = None, None
    data_proj = RASTER.crs
    # data_extent = str(RASTER_DEM_DATA.extent)
    # data_proj = RASTER_DEM_DATA.spatialReference.exportToString()
    # print('extent', data_extent)
    # print('proj', data_proj)
    try:
        minmax = [10000000, 10000000, -10000000, -10000000]
        for coords in bounds:
            minmax[0] = min(minmax[0], coords[0])
            minmax[1] = min(minmax[1], coords[1])
            minmax[2] = max(minmax[2], coords[0])
            minmax[3] = max(minmax[3], coords[1])
        print('++++++++++++++++++++++++++++++++++++++++++')
        print('minmax', minmax)
        mask_path = [[minmax[0], minmax[1]], [minmax[0], minmax[3]], [minmax[2], minmax[3]], [minmax[2], minmax[1]]]
        print(PROJ_TRANSFORMER)
        for i in range(len(mask_path)):
            mask_path[i] = PROJ_TRANSFORMER.transform(mask_path[i][0], mask_path[i][1])
        mask_pgon = shapely.geometry.Polygon(mask_path)
        print('mask_pgon', mask_pgon)
        [mask_result, affine_transf] = mask(RASTER, [mask_pgon], all_touched = True, crop=True)
        data_list = mask_result[0]
        ex0 = affine_transf * (0,0)
        ex1 = affine_transf * (len(data_list[0]), len(data_list))
        data_extent = ' '.join([
            str(min(ex0[0], ex1[0])), str(min(ex0[1], ex1[1])), 
            str(max(ex0[0], ex1[0])), str(max(ex0[1], ex1[1]))
        ])
        # for i in range(len(minmax)):
        #     minmax[i] = str(minmax[i])
        # DEM = arcpy.Clip_management(RASTER_DEM, ' '.join(minmax), "./temp_result/cut_uwind_" + session + '.tif', "#", "#", "NONE")
        # DEM = arcpy.Raster( "./temp_result/cut_uwind_" + session + '.tif')
        # data_array = arcpy.RasterToNumPyArray("./temp_result/cut_uwind_" + session + '.tif', nodata_to_value=0)
        # data_list = data_array.tolist()
        # data_extent = str(DEM.extent)
        # print('data_extent', data_extent)
        # data_proj = DEM.spatialReference.exportToString()
    except Exception as ex:
        print('ERROR:', ex)

    # if arcpy.Exists("in_memory"):
    #     arcpy.Delete_management("in_memory")
    # arcpy.Delete_management("./temp_result/cut_uwind_" + session + '.tif')
    # gc.collect()

    return {
        "data": data_list,
        "extent": data_extent,
        "proj": data_proj,
        "nodata": 0
    }

r = run_urban_wind([[103.85013338092038,1.2941103414351858],[103.85087152536515,1.297250202247156],[103.85579820635985,1.2966325253827478],[103.8552660576629,1.2939044493449927],[103.85013338092038,1.2941103414351858]])

