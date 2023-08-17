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
import time
import traceback
from PIL import Image
import numpy as np

BUFFER_AREA_DIST = 200
BUFFER_AREA_DIST_SQR = BUFFER_AREA_DIST * BUFFER_AREA_DIST
TOTAL_AREA = BUFFER_AREA_DIST_SQR * math.pi
DEG_INTERVAL = 0.25
ANGLE_INTERVAL = DEG_INTERVAL * math.pi / 180
COEFFICIENT_POWER = 2

def analyze_sensor(sensor, fa_mask_result, fa_affine_transf,
                    bd_mask_result, bd_affine_transf,
                    sim_mask_result, sim_affine_transf):
    start = time.process_time()
    # your code here

    sim_pos = sensor[0]
    coord_pos = sim_affine_transf * sim_pos
    fa_pos = ~fa_affine_transf * coord_pos
    fa_pos_int = (math.floor(fa_pos[0]), math.floor(fa_pos[1]))
    sensor_result = 0
    if int(sensor[1]) == sensor[1]:
        if (bd_mask_result[0][fa_pos_int[0]][fa_pos_int[1]] and
            bd_mask_result[0][fa_pos_int[0]][fa_pos_int[1] + 1] and
            bd_mask_result[0][fa_pos_int[0] + 1][fa_pos_int[1]] and
                bd_mask_result[0][fa_pos_int[0] + 1][fa_pos_int[1] + 1]):
            # print('!!!!!!!!!!!!!!!', (time.process_time() - start))
            return None
    else:
        if bd_mask_result[0][fa_pos_int[0]][fa_pos_int[1]]:
            # print('!!!!!!!!!!!!!!!', (time.process_time() - start))
            return None
    area_count = 0
    pixel_check = {}
    dir_count = 0

    for angle_interval_index in range(round(360 / DEG_INTERVAL)):
        dir_count += 1
        angle = ANGLE_INTERVAL * angle_interval_index
        x = math.sin(angle)
        y = math.cos(angle)
        # calculate distance & unit direction vector
        fa_x_unit = x / 2
        fa_y_unit = y / 2

        check = 2

        # check if the direction from the sensor to the pixel is obstructed
        for n in range(BUFFER_AREA_DIST * 5):
            n_x = math.floor(fa_pos_int[0] + fa_x_unit * n)
            n_y = math.floor(fa_pos_int[1] + fa_y_unit * n)

            fa_nx_dir = n_x + 0.5 - fa_pos[0]
            fa_ny_dir = n_y + 0.5 - fa_pos[1]
            # squared distance from the pixel to the sensor
            ndist_sqr = fa_nx_dir * fa_nx_dir + fa_ny_dir * fa_ny_dir

            if ndist_sqr > BUFFER_AREA_DIST_SQR: break
            pos_str = str(n_x) + '_' + str(n_y)
            if pos_str in pixel_check:
                if check and bd_mask_result[0][n_x][n_y] > 0:
                    if fa_mask_result[0][n_x][n_y] > 0 and pixel_check[pos_str] != 255:
                        # calculate distance & unit direction vector
                        weighted_frontal_area = fa_mask_result[0][n_x][n_y]
                        ndist = math.sqrt(ndist_sqr)
                        distance_coefficient = (BUFFER_AREA_DIST - ndist) / BUFFER_AREA_DIST
                        r = (distance_coefficient ** COEFFICIENT_POWER) * weighted_frontal_area
                        sensor_result += r
                        pixel_check[pos_str] = 255
                    check -= 1
                    if check == 0: break
                continue
            if bd_mask_result[0][n_x][n_y] > 0:
                pixel_check[pos_str] = 40
            else:
                pixel_check[pos_str] = 20

            if check:
                area_count += 1
                pixel_check[pos_str] = 120
                if fa_mask_result[0][n_x][n_y] == 0: continue
                # calculate distance & unit direction vector
                weighted_frontal_area = fa_mask_result[0][n_x][n_y]
                ndist = math.sqrt(ndist_sqr)
                distance_coefficient = (BUFFER_AREA_DIST - ndist) / BUFFER_AREA_DIST
                r = (distance_coefficient ** COEFFICIENT_POWER) * weighted_frontal_area
                sensor_result += r
                pixel_check[pos_str] = 255
                check -= 1
                if check == 0: break

    # # iterate through each pixel within 200x200m square surrounding the sensor position
    # for x in range(int(fa_pos_int[0]) - BUFFER_AREA_DIST, int(fa_pos_int[0]) + BUFFER_AREA_DIST):
    #     for y in range(int(fa_pos_int[1]) - BUFFER_AREA_DIST, int(fa_pos_int[1]) + BUFFER_AREA_DIST):
    #         # continue if the pixel is not a frontal area
    #         if (x < 0 or y < 0 or
    #             x >= len(fa_mask_result[0]) or
    #                 y >= len(fa_mask_result[0][0])):
    #             # y >= len(fa_mask_result[0][0]) or
    #             # fa_mask_result[0][x][y] == 0):
    #             continue
    #         # direction from the sensor to the center of the pixel
    #         fa_x_dir = x + 0.5 - fa_pos[0]
    #         fa_y_dir = y + 0.5 - fa_pos[1]

    #         # squared distance from the pixel to the sensor
    #         dist_sqr = fa_x_dir * fa_x_dir + fa_y_dir * fa_y_dir

    #         # if squared distance is higher than 200*200, continue
    #         if dist_sqr > BUFFER_AREA_DIST_SQR:
    #             continue
    #         if dist_sqr <= (BUFFER_AREA_DIST_SQR - BUFFER_AREA_DIST * 3):
    #             continue
    #         dir_count += 1

    #         # if squared distance is 0 -> sensor is right under a frontal area -> no wind
    #         if dist_sqr == 0:
    #             break

    #         # calculate distance & unit direction vector
    #         dist = math.sqrt(dist_sqr)
    #         fa_x_unit = fa_x_dir / dist / 2
    #         fa_y_unit = fa_y_dir / dist / 2

    #         check = True


    #         # find number of iterations to check obstruction
    #         max_iter = 0
    #         if fa_x_unit != 0:
    #             max_iter = math.ceil(fa_x_dir / fa_x_unit)
    #         elif fa_y_unit != 0:
    #             max_iter = math.ceil(fa_y_dir / fa_y_unit)

    #         # check if the direction from the sensor to the pixel is obstructed
    #         for n in range(max_iter):
    #             n_x = math.floor(fa_pos_int[0] + fa_x_unit * n)
    #             n_y = math.floor(fa_pos_int[1] + fa_y_unit * n)
    #             pos_str = str(n_x) + '_' + str(n_y)
    #             if pos_str in pixel_check:
    #                 if check and bd_mask_result[0][n_x][n_y] > 0:
    #                     if fa_mask_result[0][n_x][n_y] > 0 and pixel_check[pos_str] != 255:
    #                         # calculate distance & unit direction vector
    #                         weighted_frontal_area = fa_mask_result[0][n_x][n_y]
    #                         fa_nx_dir = n_x + 0.5 - fa_pos[0]
    #                         fa_ny_dir = n_y + 0.5 - fa_pos[1]
    #                         # squared distance from the pixel to the sensor
    #                         ndist_sqr = fa_nx_dir * fa_nx_dir + fa_ny_dir * fa_ny_dir
    #                         ndist = math.sqrt(ndist_sqr)
    #                         distance_coefficient = (
    #                             BUFFER_AREA_DIST - ndist) / BUFFER_AREA_DIST
    #                         r = distance_coefficient * distance_coefficient * weighted_frontal_area
    #                         sensor_result += r
    #                         pixel_check[pos_str] = 255
    #                     check = False
    #                 continue
    #             if bd_mask_result[0][n_x][n_y] > 0:
    #                 pixel_check[pos_str] = 40
    #             else:
    #                 pixel_check[pos_str] = 20

    #             if check:
    #                 area_count += 1
    #                 pixel_check[pos_str] = 120
    #                 if fa_mask_result[0][n_x][n_y] == 0: continue
    #                 # calculate distance & unit direction vector
    #                 weighted_frontal_area = fa_mask_result[0][n_x][n_y]
    #                 fa_nx_dir = n_x + 0.5 - fa_pos[0]
    #                 fa_ny_dir = n_y + 0.5 - fa_pos[1]
    #                 # squared distance from the pixel to the sensor
    #                 ndist_sqr = fa_nx_dir * fa_nx_dir + fa_ny_dir * fa_ny_dir
    #                 ndist = math.sqrt(ndist_sqr)
    #                 distance_coefficient = (
    #                     BUFFER_AREA_DIST - ndist) / BUFFER_AREA_DIST
    #                 r = distance_coefficient * distance_coefficient * weighted_frontal_area
    #                 sensor_result += r
    #                 pixel_check[pos_str] = 255
    #                 check = False

    #             if n_x == x and n_y == y:
    #                 break
    #         pos_str = str(x) + '_' + str(y)

    #         if check and pos_str not in pixel_check and fa_mask_result[0][x][y] > 0:
    #             weighted_frontal_area = fa_mask_result[0][x][y]
    #             distance_coefficient = (
    #                 BUFFER_AREA_DIST - dist) / BUFFER_AREA_DIST
    #             r = distance_coefficient * distance_coefficient * weighted_frontal_area
    #             sensor_result += r
    #             pixel_check[pos_str] = 255
    #             area_count += 1

    missing_count = 0
    # xdim = int(fa_pos_int[0]) + BUFFER_AREA_DIST - (int(fa_pos_int[0]) - BUFFER_AREA_DIST)
    # ydim = int(fa_pos_int[1]) + BUFFER_AREA_DIST - (int(fa_pos_int[1]) - BUFFER_AREA_DIST)
    # test_check = np.full((xdim,ydim), 0)
    # for x in range(int(fa_pos_int[0]) - BUFFER_AREA_DIST, int(fa_pos_int[0]) + BUFFER_AREA_DIST):
    #     ax = x - (int(fa_pos_int[0]) - BUFFER_AREA_DIST)
    #     for y in range(int(fa_pos_int[1]) - BUFFER_AREA_DIST, int(fa_pos_int[1]) + BUFFER_AREA_DIST):
    #         ay = y - (int(fa_pos_int[1]) - BUFFER_AREA_DIST)
    #         pos_str = str(x) + '_' + str(y)
    #         if pos_str not in pixel_check:
    #             xd = x + 0.5 - fa_pos[0]
    #             yd = y + 0.5 - fa_pos[1]
    #             # squared distance from the pixel to the sensor
    #             d_sqr = xd * xd + yd * yd
    #             if d_sqr > BUFFER_AREA_DIST_SQR: continue

    #             missing_count += 1
    #             pass
    #             # test_check[ax][ay] = 0x000000
    #             # print('_____ missing pos', pos_str)
    #         else:
    #             test_check[ax][ay] = pixel_check[pos_str]
    # test_check[BUFFER_AREA_DIST][BUFFER_AREA_DIST] = 255
    # test_check[BUFFER_AREA_DIST + 1][BUFFER_AREA_DIST - 1] = 255
    # test_check[BUFFER_AREA_DIST + 1][BUFFER_AREA_DIST + 1] = 255
    # test_check[BUFFER_AREA_DIST - 1][BUFFER_AREA_DIST + 1] = 255
    # test_check[BUFFER_AREA_DIST - 1][BUFFER_AREA_DIST - 1] = 255
    # im = Image.fromarray(test_check)
    # im = im.convert('RGB')
    # im.save("./test/test" + str(start) + ".png")

    # console.log('_ FAD:', FAD)
    # const VR = -1.64 * FAD + 0.28
    # console.log('_ VR:', VR)
    # results0.push(VR)
    FAD = sensor_result / area_count
    # FAD = FAD * 12
    print('___ FAD:', FAD, '; dir_count:', dir_count, '; missing_count:', missing_count, '; time taken:', (time.process_time() - start))
    VR = -1.64 * FAD + 0.28
    if VR < 0:
        VR = 0
    # print('    VR ', VR)
    return [sensor[1], sensor[2], VR]

def run_wind_sensor(sensors, fa_mask_result, fa_affine_transf,
                    bd_mask_result, bd_affine_transf,
                    sim_mask_result, sim_affine_transf):
    sensor_results = []
    # data_extent = None
    # data_proj = str(RASTER.crs)
    # half_grid = grid_size / 2

    try:
        # fa_mask_pgon = shapely.geometry.Polygon(fa_mask_path)
        # sim_mask_pgon = shapely.geometry.Polygon(sim_mask_path)
        # [fa_mask_result, fa_affine_transf] = mask(RASTER, [fa_mask_pgon], all_touched = True, crop=True)
        # [bd_mask_result, bd_affine_transf] = mask(BUILDING, [fa_mask_pgon], all_touched = True, crop=True)
        # [sim_mask_result, sim_affine_transf] = mask(RASTER, [sim_mask_pgon], all_touched = True, crop=True)

        # for each of the simulation tile
        for sensor in sensors:
            sensor_result = analyze_sensor(sensor, fa_mask_result, fa_affine_transf,
                                    bd_mask_result, bd_affine_transf,
                                    sim_mask_result, sim_affine_transf)
            if sensor_result is not None:
                sensor_results.append(sensor_result)

    except Exception as ex:
        print('ERROR:', ex)
        traceback.print_tb(ex.__traceback__)
    return sensor_results
    # return {
    #     "data": data_list,
    #     "extent": data_extent,
    #     "proj": data_proj,
    #     "nodata": 0
    # }


def run_wind_worker(input_str):
    print('______ starting sim task ______')
    start = time.process_time()

    # input = json.loads(input_str)
    input = input_str
    sensors = input['sensors']

    fa_mask_result = input['fa_mask_result']
    fa_affine_transf = input['fa_affine_transf']
    bd_mask_result = input['bd_mask_result']
    bd_affine_transf = input['bd_affine_transf']
    sim_mask_result = input['sim_mask_result']
    sim_affine_transf = input['sim_affine_transf']

    result = run_wind_sensor(sensors,
                             fa_mask_result, fa_affine_transf,
                             bd_mask_result, bd_affine_transf,
                             sim_mask_result, sim_affine_transf)
    print('task ending, time taken:', (time.process_time() - start))
    return result


