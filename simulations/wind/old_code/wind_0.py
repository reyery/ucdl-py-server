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
import traceback

import rasterio
from rasterio.mask import mask
import shapely
from pyproj import Transformer, CRS

from .wind_data import sg_wind, sg_wind_stn_data

RASTER_DEM= os.path.join(os.path.dirname(__file__), "FA.tif")
# RASTER_DEM_DATA=arcpy.Raster(RASTER_DEM)
RASTER = rasterio.open(RASTER_DEM)
BUILDING_TIF= os.path.join(os.path.dirname(__file__), "building.tif")
BUILDING = rasterio.open(BUILDING_TIF)
PROJ_TRANSFORMER = Transformer.from_crs('EPSG:4326', 'EPSG:3414', always_xy=True)
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
    WIND_DIR_VECS.append([x,y])


def run_wind(bounds, grid_size):
    data_list=[]
    data_extent = None
    data_proj = str(RASTER.crs)
    half_grid = grid_size / 2
    wind_rose = sg_wind['S24']

    try:
        # find the min/max coordinates of the simulation boundary
        minmax = [10000000, 10000000, -10000000, -10000000]
        transf_bound = []
        for coords in bounds:
            minmax[0] = min(minmax[0], coords[0])
            minmax[1] = min(minmax[1], coords[1])
            minmax[2] = max(minmax[2], coords[0])
            minmax[3] = max(minmax[3], coords[1])
            transf_bound.append(PROJ_TRANSFORMER.transform(coords[0], coords[1]))

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
        bound_pgon = shapely.geometry.Polygon(transf_bound)
        print('____transf_bound', transf_bound)
        [fa_mask_result, fa_affine_transf] = mask(RASTER, [fa_mask_pgon], all_touched = True, crop=True)
        [bd_mask_result, bd_affine_transf] = mask(BUILDING, [fa_mask_pgon], all_touched = True, crop=True)
        [sim_mask_result, sim_affine_transf] = mask(RASTER, [sim_mask_pgon], all_touched = True, crop=True)
        fa_bottom_left = fa_affine_transf * (0,0)
        sim_bottom_left = sim_affine_transf * (0,0)

        sensors = []
        for i in range(math.ceil(len(sim_mask_result[0])/grid_size)):
            row = []
            for j in range(math.ceil(len(sim_mask_result[0][0])/grid_size)):
                row.append(0)
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
                        print(coord_pos[0], coord_pos[1])
                        sensors.append([(i * grid_size + half_grid, j * grid_size + half_grid), i, j])
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
        for sensor in sensors:
            sim_pos = sensor[0]
            coord_pos = sim_affine_transf * sim_pos
            fa_pos = ~fa_affine_transf * coord_pos
            fa_pos_int = (math.floor(fa_pos[0]), math.floor(fa_pos[1]))
            sensor_result = 0
            break_check = False
            data_list[sensor[1]][sensor[2]] = 0.0001
            # if int(sensor[1]) == sensor[1]:
            #     if (bd_mask_result[0][fa_pos_int[0]][fa_pos_int[1]] and 
            #         bd_mask_result[0][fa_pos_int[0]][fa_pos_int[1] + 1] and 
            #         bd_mask_result[0][fa_pos_int[0] + 1][fa_pos_int[1]] and 
            #         bd_mask_result[0][fa_pos_int[0] + 1][fa_pos_int[1] + 1]):
            #         print('!!!!!!!!!!!!!!!')
            #         continue
            # else:
            #     if bd_mask_result[0][fa_pos_int[0]][fa_pos_int[1]]:
            #         print('!!!!!!!!!!!!!!!')
            #         continue

            point_wind = {}
            area_count = 0
            # iterate through each pixel within 200x200m square surrounding the sensor position
            for x in range(int(fa_pos_int[0]) - BUFFER_AREA_DIST, int(fa_pos_int[0]) + BUFFER_AREA_DIST):
                for y in range(int(fa_pos_int[1]) - BUFFER_AREA_DIST, int(fa_pos_int[1]) + BUFFER_AREA_DIST):
                    # continue if the pixel is not a frontal area
                    if (x < 0 or y < 0 or 
                        x >= len(fa_mask_result[0]) or 
                        # y >= len(fa_mask_result[0][0])):
                        y >= len(fa_mask_result[0][0]) or
                        fa_mask_result[0][x][y] == 0):
                            continue
                    # direction from the sensor to the center of the pixel
                    fa_x_dir = x + 0.5 - fa_pos[0]
                    fa_y_dir = y + 0.5 - fa_pos[1]

                    # squared distance from the pixel to the sensor
                    dist_sqr = fa_x_dir * fa_x_dir + fa_y_dir * fa_y_dir

                    # if squared distance is higher than 200*200, continue
                    if dist_sqr > BUFFER_AREA_DIST_SQR: continue

                    # if squared distance is 0 -> sensor is right under a frontal area -> no wind
                    if dist_sqr == 0: 
                        break_check = True
                        break

                    # calculate distance & unit direction vector
                    dist = math.sqrt(dist_sqr)
                    fa_x_unit = fa_x_dir / dist
                    fa_y_unit = fa_y_dir / dist



                    check = True

                    # find number of iterations to check obstruction
                    max_iter = 0
                    if fa_x_unit != 0:
                        max_iter = math.ceil(fa_x_dir / fa_x_unit)
                    elif fa_y_unit != 0:
                        max_iter = math.ceil(fa_y_dir / fa_y_unit)

                    # check if the direction from the sensor to the pixel is obstructed
                    for n in range(max_iter):
                        n_x = math.floor(fa_pos_int[0] + fa_x_unit * n)
                        n_y = math.floor(fa_pos_int[1] + fa_y_unit * n)
                        if n_x == x and n_y == y: break
                        if fa_mask_result[0][n_x][n_y] > 0:
                            area_count += 1
                            check = False
                            pos_str = str(n_x) + '_' + str(n_y)
                            if pos_str in point_wind:
                                sensor_result += point_wind[pos_str]
                                break
                            fa_x_dir_ints = n_x + 0.5 - fa_pos[0]
                            fa_y_dir_ints = n_y + 0.5 - fa_pos[1]
                            n_dist = math.sqrt(fa_x_dir_ints * fa_x_dir_ints + fa_y_dir_ints * fa_y_dir_ints)

                            wind_freq = 0
                            for dirIndex in range(len(WIND_DIR_VECS)):
                                windDir = WIND_DIR_VECS[dirIndex]
                                obst = False
                                for c in range(1, MIN_WIND_DIST + 1):
                                    wCoord = [math.floor(windDir[0] * c + n_x + 0.5), math.floor(windDir[1] * c + n_y + 0.5)]
                                    if wCoord[0] == x and wCoord[1] == y: continue
                                    if bd_mask_result[0][wCoord[0]][wCoord[1]]:
                                        obst = True
                                        break
                                if obst:
                                    wind_freq += wind_rose[dirIndex]
                            weighted_frontal_area = wind_freq * fa_mask_result[0][n_x][n_y]
                            # weighted_frontal_area = fa_mask_result[0][n_x][n_y]
                            distance_coefficient = (BUFFER_AREA_DIST - n_dist) / BUFFER_AREA_DIST
                            r = distance_coefficient * distance_coefficient * weighted_frontal_area
                            point_wind[pos_str] = r
                            sensor_result += r
                            break
                    
                    # if not obstructed
                    if check:
                        pos_str = str(x) + '_' + str(y)
                        area_count += 1
                        if pos_str in point_wind:
                            sensor_result += point_wind[pos_str]
                            break
                        else:
                            wind_freq = 0
                            for dirIndex in range(len(WIND_DIR_VECS)):
                                windDir = WIND_DIR_VECS[dirIndex]
                                obst = False
                                for c in range(1, MIN_WIND_DIST + 1):
                                    wCoord = [math.floor(windDir[0] * c + x + 0.5), math.floor(windDir[1] * c + y + 0.5)]
                                    if wCoord[0] == x and wCoord[1] == y: continue
                                    if bd_mask_result[0][wCoord[0]][wCoord[1]]:
                                        obst = True
                                        break
                                if obst:
                                    wind_freq += wind_rose[dirIndex]

                            # dirAngle = math.atan2(fa_x_dir, fa_y_dir) * 180 / math.pi
                            # if dirAngle < -10 :
                            #     dirAngle += 360
                            # freqIndex = math.floor((dirAngle + 10) / 22.5)
                            # wind_freq = wind_rose[freqIndex]

                            weighted_frontal_area = wind_freq * fa_mask_result[0][x][y]
                            # weighted_frontal_area = fa_mask_result[0][x][y]
                            distance_coefficient = (BUFFER_AREA_DIST - dist) / BUFFER_AREA_DIST
                            r = distance_coefficient * distance_coefficient * weighted_frontal_area
                            sensor_result += r
                            area_count += 1
                            point_wind[pos_str] = r

                        # print(weighted_frontal_area, distance_coefficient, r)
                if break_check: break
            if break_check:
                data_list[sensor[1]][sensor[2]] = 0.001
            else:
                # console.log('_ FAD:', FAD)
                # const VR = -1.64 * FAD + 0.28
                # console.log('_ VR:', VR)
                # results0.push(VR)
                FAD = sensor_result / area_count
                FAD = FAD / 25
                print('___ FAD', FAD)
                VR = -1.64 * FAD + 0.28
                if VR <= 0: VR = 0.001
                # print('    VR ', VR)
                data_list[sensor[1]][sensor[2]] = VR
        ex0 = sim_affine_transf * (0,0)
        ex1 = sim_affine_transf * (len(data_list[0]) * grid_size, len(data_list) * grid_size)
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
        "nodata": 0
    }



