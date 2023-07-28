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
import sys
import json
import gc
import time 
import os

import rasterio
from rasterio.mask import mask
import shapely
from pyproj import Transformer, CRS


RASTER_DEM= os.path.join(os.path.dirname(__file__), "FA.tif")
# RASTER_DEM_DATA=arcpy.Raster(RASTER_DEM)
RASTER = rasterio.open(RASTER_DEM)
PROJ_TRANSFORMER = Transformer.from_crs('EPSG:4326', 'EPSG:3414', always_xy=True)
BUFFER_AREA_DIST = 200


def run_wind(bounds, grid_size):
    data_list=[]
    data_extent = None
    data_proj = str(RASTER.crs)

    try:
        # find the min/max coordinates of the simulation boundary
        minmax = [10000000, 10000000, -10000000, -10000000]
        for coords in bounds:
            minmax[0] = min(minmax[0], coords[0])
            minmax[1] = min(minmax[1], coords[1])
            minmax[2] = max(minmax[2], coords[0])
            minmax[3] = max(minmax[3], coords[1])

        # create a masking path for the boundary
        sim_mask_path = [[minmax[0], minmax[1]], [minmax[0], minmax[3]], [minmax[2], minmax[3]], [minmax[2], minmax[1]]]
        for i in range(len(sim_mask_path)):
            sim_mask_path[i] = PROJ_TRANSFORMER.transform(sim_mask_path[i][0], sim_mask_path[i][1])
        fa_mask_path = [
            [sim_mask_path[0][0] - 200, sim_mask_path[0][1] - 200],
            [sim_mask_path[1][0] - 200, sim_mask_path[1][1] + 200],
            [sim_mask_path[2][0] + 200, sim_mask_path[2][1] + 200],
            [sim_mask_path[3][0] + 200, sim_mask_path[3][1] - 200]
        ]

        fa_mask_pgon = shapely.geometry.Polygon(fa_mask_path)
        sim_mask_pgon = shapely.geometry.Polygon(sim_mask_path)
        [fa_mask_result, fa_affine_transf] = mask(RASTER, [fa_mask_pgon], all_touched = True, crop=True)
        [sim_mask_result, sim_affine_transf] = mask(RASTER, [sim_mask_pgon], all_touched = True, crop=True)
        fa_bottom_left = fa_affine_transf * (0,0)
        sim_bottom_left = sim_affine_transf * (0,0)

        print('-------------------------------------------------')
        print('_____________ fa_mask_result')
        print(fa_mask_result[0])
        print(len(fa_mask_result[0]), len(fa_mask_result[0][0]))
        print(fa_affine_transf)
        print(fa_bottom_left)
        print('_____________ sim_mask_result')
        print(sim_mask_result[0])
        print(len(sim_mask_result[0]), len(sim_mask_result[0][0]))
        print(sim_affine_transf)
        print(sim_bottom_left)
        print(grid_size)
        half_grid = grid_size / 2
        for i in range(math.ceil(len(sim_mask_result[0])/grid_size)):
            for j in range(math.ceil(len(sim_mask_result[0][0])/grid_size)):
                print(i * grid_size + half_grid, j * grid_size + half_grid)
        # data_list = mask_result[0].tolist()
        # ex0 = affine_transf * (0,0)
        # ex1 = affine_transf * (len(data_list[0]), len(data_list))
        # data_extent = ' '.join([
        #     str(min(ex0[0], ex1[0])), str(min(ex0[1], ex1[1])), 
        #     str(max(ex0[0], ex1[0])), str(max(ex0[1], ex1[1]))
        # ])
    except Exception as ex:
        print('ERROR:', ex)

    return {
        "data": data_list,
        "extent": data_extent,
        "proj": data_proj,
        "nodata": 0
    }