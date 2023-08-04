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
import time
import traceback
from multiprocessing import Pool
from PIL import Image
import numpy as np
import rasterio
from rasterio.mask import mask
import shapely
from pyproj import Transformer, CRS

from .wind_sim import run_wind_worker
from .wind_data import sg_wind, sg_wind_stn_data

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

def run_wind(bounds, grid_size):
    data_list = []
    data_extent = None
    data_proj = str(RASTER.crs)
    half_grid = grid_size / 2

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
            [sim_mask_path[0][0] - 200, sim_mask_path[0][1] - 200],
            [sim_mask_path[1][0] - 200, sim_mask_path[1][1] + 200],
            [sim_mask_path[2][0] + 200, sim_mask_path[2][1] + 200],
            [sim_mask_path[3][0] + 200, sim_mask_path[3][1] - 200]
        ]

        fa_mask_pgon = shapely.geometry.Polygon(fa_mask_path)
        sim_mask_pgon = shapely.geometry.Polygon(sim_mask_path)
        bound_pgon = shapely.geometry.Polygon(transf_bound)
        [fa_mask_result, fa_affine_transf] = mask(
            RASTER, [fa_mask_pgon], all_touched=True, crop=True)
        [bd_mask_result, bd_affine_transf] = mask(
            BUILDING, [fa_mask_pgon], all_touched=True, crop=True)
        [sim_mask_result, sim_affine_transf] = mask(
            RASTER, [sim_mask_pgon], all_touched=True, crop=True)
        fa_bottom_left = fa_affine_transf * (0, 0)
        sim_bottom_left = sim_affine_transf * (0, 0)

        sensors = []
        for i in range(math.ceil(len(sim_mask_result[0])/grid_size)):
            row = []
            for j in range(math.ceil(len(sim_mask_result[0][0])/grid_size)):
                row.append(-1)
                sim_pos = [
                    [j * grid_size,             i * grid_size],
                    [j * grid_size,             i * grid_size + grid_size],
                    [j * grid_size + grid_size, i * grid_size],
                    [j * grid_size + grid_size, i * grid_size + grid_size]
                ]
                for pos in sim_pos:
                    coord_pos = sim_affine_transf * pos
                    pt = shapely.geometry.Point(coord_pos[0], coord_pos[1])
                    if bound_pgon.contains(pt):
                        sensors.append([(i * grid_size + half_grid, j * grid_size + half_grid), i, j])
                        row[-1] = 0
                        break
            data_list.append(row)
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
        print(grid_size)
        # for each of the simulation tile

        n = math.ceil(len(sensors) / NUM_WORKERS) if math.ceil(len(sensors) /
                                                               NUM_WORKERS) < TASKS_PER_WORKER else TASKS_PER_WORKER
        sensors_worker_data = []
        for i in range(0, len(sensors), n):
            end = (i + n) if (i + n <= len(sensors)) else len(sensors)
            sensors_worker_data.append({
                'sensors': sensors[i:end],
                'fa_mask_result': fa_mask_result,
                'fa_affine_transf': fa_affine_transf,
                'bd_mask_result': bd_mask_result,
                'bd_affine_transf': bd_affine_transf,
                'sim_mask_result': sim_mask_result,
                'sim_affine_transf': sim_affine_transf
            })
        with Pool(NUM_WORKERS) as POOL:
            results = POOL.map(run_wind_worker, sensors_worker_data)
        for thread_result in results:
            for r in thread_result:
                data_list[r[0]][r[1]] = r[2]

        ex0 = sim_affine_transf * (0, 0)
        ex1 = sim_affine_transf * \
            (len(data_list[0]) * grid_size, len(data_list) * grid_size)
        data_extent = ' '.join([
            str(min(ex0[0], ex1[0])), str(min(ex0[1], ex1[1])),
            str(max(ex0[0], ex1[0])), str(max(ex0[1], ex1[1]))
        ])
    except Exception as ex:
        print('ERROR:', ex)
        traceback.print_tb(ex.__traceback__)

    return {
        "data": data_list,
        "extent": data_extent,
        "proj": data_proj,
        "nodata": -1
    }
