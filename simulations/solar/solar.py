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
import math
import os
import numpy as np

import rasterio
from rasterio.mask import mask
import shapely
from pyproj import Transformer, CRS
from ..util.aggregate import aggregate


RASTER_DEM= os.path.join(os.path.dirname(__file__), "raster", "solar.tif")
RASTER = rasterio.open(RASTER_DEM)
PROJ_TRANSFORMER = Transformer.from_crs('EPSG:4326', 'EPSG:3414', always_xy=True)

def run_solar(bounds, grid_size):
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

        minmax[0], minmax[1] = PROJ_TRANSFORMER.transform(minmax[0], minmax[1])
        minmax[2], minmax[3] = PROJ_TRANSFORMER.transform(minmax[2], minmax[3])

        if grid_size > 1:
            minmax[2] = math.ceil((minmax[2] - minmax[0]) / grid_size) * grid_size + minmax[0] - 1
            minmax[3] = math.ceil((minmax[3] - minmax[1]) / grid_size) * grid_size + minmax[1] - 1

        mask_path = [[minmax[0], minmax[1]], [minmax[0], minmax[3]], [minmax[2], minmax[3]], [minmax[2], minmax[1]]]

        mask_pgon = shapely.geometry.Polygon(mask_path)

        [mask_result, affine_transf] = mask(RASTER, [mask_pgon], all_touched = True, crop=True)

        data_list = mask_result[0].tolist()
        ex0 = affine_transf * (0,0)
        ex1 = affine_transf * (len(data_list[0]), len(data_list))
        data_extent = ' '.join([
            str(min(ex0[0], ex1[0])), str(min(ex0[1], ex1[1])), 
            str(max(ex0[0], ex1[0])), str(max(ex0[1], ex1[1]))
        ])
        if grid_size > 1:
            data_list = aggregate(data_list, grid_size, "mean")
    except Exception as ex:
        print('ERROR:', ex)

    return {
        "data": data_list,
        "extent": data_extent,
        "proj": data_proj,
        "nodata": 0
    }

