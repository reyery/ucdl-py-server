#!/opt/local/bin/python2.7
##
# A python code to calculate AH dispersion
##
# Due to SSL certificate problem, this script has to be run with some version of python > 2.7.6
##
# Written by He Wenhui at FRS, Finished on August 24, 2021
# import arcpy
# from arcpy import env
# from arcpy.sa import *
# from arcpy.ia import *
import math
import os
import traceback
import rasterio
from rasterio.mask import mask
import shapely
from pyproj import Transformer

NUM_WORKERS = 5
# NUM_WORKERS = 1
TASKS_PER_WORKER = 50
RASTER_DEM = os.path.join(os.path.dirname(__file__), "FA.tif")
# RASTER_DEM_DATA=arcpy.Raster(RASTER_DEM)
RASTER = rasterio.open(RASTER_DEM)
BUILDING_TIF = os.path.join(os.path.dirname(__file__), "building.tif")
BUILDING = rasterio.open(BUILDING_TIF)
PROJ_TRANSFORMER = Transformer.from_crs(
    'EPSG:4326', 'EPSG:3414', always_xy=True)
BUFFER_AREA_DIST = 200
BUFFER_AREA_DIST_SQR = BUFFER_AREA_DIST * BUFFER_AREA_DIST
TOTAL_AREA = BUFFER_AREA_DIST_SQR * math.pi
MIN_WIND_DIST = 5
WIND_DIR_VECS = []
for i in range(16):
    angle = i * 22.5 * math.pi / 180
    cs = math.cos(angle)
    sn = math.sin(angle)

    x = sn * 0.5
    y = cs * 0.5
    WIND_DIR_VECS.append([x, y])
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')


def run_wind_clip(bounds, grid_size):
    data_extent = None
    data_proj = str(RASTER.crs)

    try:
        # find the min/max coordinates of the simulation boundary
        minmax = [10000000, 10000000, -10000000, -10000000]
        transf_bound = []
        for coords in bounds:
            minmax[0] = min(minmax[0], coords[0])
            minmax[1] = min(minmax[1], coords[1])
            minmax[2] = max(minmax[2], coords[0])
            minmax[3] = max(minmax[3], coords[1])
            transf_bound.append(
                PROJ_TRANSFORMER.transform(coords[0], coords[1]))

        # create a masking path for the boundary
        sim_mask_path = [[minmax[0], minmax[1]], [minmax[0], minmax[3]], [
            minmax[2], minmax[3]], [minmax[2], minmax[1]]]
        for i in range(len(sim_mask_path)):
            sim_mask_path[i] = PROJ_TRANSFORMER.transform(
                sim_mask_path[i][0], sim_mask_path[i][1])
        fa_mask_path = [
            [sim_mask_path[0][0] - (BUFFER_AREA_DIST + 1), sim_mask_path[0][1] - (BUFFER_AREA_DIST + 1)],
            [sim_mask_path[1][0] - (BUFFER_AREA_DIST + 1), sim_mask_path[1][1] + (BUFFER_AREA_DIST + 1)],
            [sim_mask_path[2][0] + (BUFFER_AREA_DIST + 1), sim_mask_path[2][1] + (BUFFER_AREA_DIST + 1)],
            [sim_mask_path[3][0] + (BUFFER_AREA_DIST + 1), sim_mask_path[3][1] - (BUFFER_AREA_DIST + 1)]
        ]
        fa_mask_pgon = shapely.geometry.Polygon(fa_mask_path)
        sim_mask_pgon = shapely.geometry.Polygon(sim_mask_path)
        [fa_mask_result, fa_affine_transf] = mask(
            RASTER, [fa_mask_pgon], all_touched=True, crop=True)
        [bd_mask_result, bd_affine_transf] = mask(
            BUILDING, [fa_mask_pgon], all_touched=True, crop=True)
        [sim_mask_result, sim_affine_transf] = mask(
            RASTER, [sim_mask_pgon], all_touched=True, crop=True)
        fa_bottom_left = fa_affine_transf * (0, 0)
        sim_bottom_left = sim_affine_transf * (0, 0)


        print('-------------------------------------------------')
        print('_____________ fa_mask_result')
        print(len(fa_mask_result[0]), len(fa_mask_result[0][0]))
        print(fa_affine_transf)
        print(fa_bottom_left)
        print('_____________ bd_mask_result')
        print(bd_mask_result)
        print(len(bd_mask_result[0]), len(bd_mask_result[0][0]))
        print(bd_affine_transf)
        print('_____________ sim_mask_result')
        print(len(sim_mask_result[0]), len(sim_mask_result[0][0]))
        print(sim_affine_transf)
        print(sim_bottom_left)
        print('sim_bottom_left[0]', sim_bottom_left[0], sim_bottom_left[1])
        for i in range(len(transf_bound)):
            print('transf_bound[i]', transf_bound[i])
            # transf_bound[i] = [
            #     transf_bound[i][0] - sim_bottom_left[0],
            #     transf_bound[i][1] - sim_bottom_left[1]
            # ]

        ex0 = sim_affine_transf * (0, 0)
        ex1 = sim_affine_transf * (
            math.ceil(len(sim_mask_result[0][0])/grid_size) * grid_size, 
            math.ceil(len(sim_mask_result[0])/grid_size) * grid_size
        )
        data_extent = [
            min(ex0[0], ex1[0]), min(ex0[1], ex1[1]),
            max(ex0[0], ex1[0]), max(ex0[1], ex1[1])
        ]

        # for each of the simulation tile
        return {
            "fa_mask_result": fa_mask_result[0].tolist(),
            "bd_mask_result": bd_mask_result[0].tolist(),
            "sim_mask_result": sim_mask_result[0].tolist(),

            "fa_affine_transf": [i for i in fa_affine_transf],
            "sim_affine_transf": [i for i in sim_affine_transf],

            "fa_bottom_left": fa_bottom_left,
            "sim_bottom_left": sim_bottom_left,

            "transf_bound": transf_bound,
            "extent": data_extent,
            "proj": data_proj,
            "nodata": -1,
            "success": True
        }

    except Exception as ex:
        print('ERROR:', ex)
        traceback.print_tb(ex.__traceback__)

    return { "success": False }
