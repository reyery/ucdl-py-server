# import arcpy
# from arcpy import env
# from arcpy.sa import *
# import math
# import time
# import numpy
# import gc
# import sys
# import os
# import shutil
# import xlwt
# from scipy.interpolate import interp1d
# import multiprocessing
# from .sg_wind_all import WIND_DATA

# global pi
# pi = math.pi
# global EPSILON
# EPSILON = 0.00001
# global MAX_LAYER_NUMBER
# MAX_LAYER_NUMBER = 0
# WIND_DIRECTIONS=['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']

# TEMP_FOLDER = './temp_result'

# def afdx1(DEM_array,m,n,WINDDIRECTION_angle,WINDDIRECTION_theta, MAXHEIGHT):
#     h=DEM_array[m, n]
#     if h >= MAXHEIGHT:h = MAXHEIGHT
#     afdx1=0
#     if (WINDDIRECTION_angle>0) and (WINDDIRECTION_angle<180):
#         afdx1 = abs(Sin(WINDDIRECTION_theta)) * h
#     return afdx1


# def afdx2(DEM_array,m,n,WINDDIRECTION_angle,WINDDIRECTION_theta, MAXHEIGHT):
#     h=DEM_array[m, n]
#     if h >= MAXHEIGHT:h = MAXHEIGHT
#     afdx2=0
#     if (WINDDIRECTION_angle>180) and (WINDDIRECTION_angle<360):
#         afdx2 = abs(Sin(WINDDIRECTION_theta)) * h
#     return afdx2


# def afdy1(DEM_array,m,n,WINDDIRECTION_angle,WINDDIRECTION_theta, MAXHEIGHT):
#     h=DEM_array[m, n]
#     if h >= MAXHEIGHT:h = MAXHEIGHT
#     afdy1=0
#     if (WINDDIRECTION_angle>90) and (WINDDIRECTION_angle<270):
#         afdy1 = abs(Cos(WINDDIRECTION_theta)) * h 
#     return afdy1

# def afdy2(DEM_array,m,n,WINDDIRECTION_angle,WINDDIRECTION_theta, MAXHEIGHT):
#     h=DEM_array[m, n]
#     if h >= MAXHEIGHT:h = MAXHEIGHT
#     afdy2=0
#     if (WINDDIRECTION_angle>270) or (WINDDIRECTION_angle<90):
#         afdy2 =abs(Cos(WINDDIRECTION_theta)) * h
#     return afdy2

# def afd(DEM_array,m,n,Tile_DEM_height,Tile_DEM_width,WINDDIRECTION_angle,WINDDIRECTION_theta, MAXHEIGHT):
#     h=DEM_array[m, n]
#     if h >= MAXHEIGHT:h = MAXHEIGHT
#     afd = 0
    
#     if math.sin(WINDDIRECTION_theta)>0:dx = 1
#     elif math.sin(WINDDIRECTION_theta)<0 : dx=-1
#     else:dx=0
    
#     if math.cos(WINDDIRECTION_theta)>0:dy=-1
#     elif math.cos(WINDDIRECTION_theta)<0: dy=1
#     else:dy=0

#     x=m+dx
#     y=n+dy

#     if((x >= 0) & (x <= Tile_DEM_height - 1)):
#         hdx = DEM_array[x, n]
#         #print(hdx)
#         if (hdx >= MAXHEIGHT): hdx = MAXHEIGHT
#         if ((round(h,4) - round(hdx,4))> EPSILON):afd = afd + abs(Sin(WINDDIRECTION_theta)) * (h - hdx)

#     if((y >= 0) & (y <= Tile_DEM_width - 1)):
#         hdy = DEM_array[m, y]
#         if (hdy >= MAXHEIGHT): hdy = MAXHEIGHT
#         if ((round(h,4) - round(hdy,4)) > EPSILON): afd = afd + abs(Cos(WINDDIRECTION_theta)) * (h - hdy)
#         #print(hdy,(h - hdy))
#     afd=round(afd,4)
#     #print(afd,h,WINDDIRECTION_angle,WINDDIRECTION_theta,Cos(WINDDIRECTION_theta))
#     return afd

# def Tile_fad(DEM_array,x_start_valid,y_start_valid,WINDDIRECTION_angle,WINDDIRECTION_theta, RESOLUTION, MAXHEIGHT):
#     Tile_DEM_width=DEM_array.shape[1]
#     Tile_DEM_height=DEM_array.shape[0]
#     Result_array=numpy.zeros((Tile_DEM_height-y_start_valid,Tile_DEM_width-x_start_valid))
#     for i in range(y_start_valid,Tile_DEM_height-y_start_valid): # notice that i is from top
#         Result_i=i
#         for j in range(x_start_valid,Tile_DEM_width-1):
#             Result_j=j-x_start_valid
#             triggerx1 = float(Tile_DEM_height-y_start_valid-Result_i - 1) / RESOLUTION
#             triggery1 = float(Result_j + 1) / RESOLUTION
#             triggerx2 = float(Tile_DEM_height-y_start_valid-Result_i) / RESOLUTION
#             triggery2 = float(Result_j) / RESOLUTION
#             if (DEM_array[i,j]>0):
#                 Result_array[Result_i, Result_j] = afd(DEM_array,i, j,Tile_DEM_height,Tile_DEM_width,WINDDIRECTION_angle,WINDDIRECTION_theta, MAXHEIGHT)
#                 #if (Result_array[Result_i, Result_j]!=0):print Result_array[Result_i, Result_j]
#                 #if (int(DEM_array[i,j])==25):print Result_array[Result_i, Result_j]
#                 if ((triggerx1 == int(triggerx1)) & (Result_array[Result_i, Result_j]==0)):
#                     Result_array[Result_i, Result_j] = afdx1(DEM_array,i, j,WINDDIRECTION_angle,WINDDIRECTION_theta, MAXHEIGHT)
#                 if ((triggery1 == int(triggery1)) & (Result_array[Result_i, Result_j]==0)):
#                     Result_array[Result_i, Result_j] = afdy1(DEM_array,i, j,WINDDIRECTION_angle,WINDDIRECTION_theta, MAXHEIGHT)
#                 if ((triggerx2 == int(triggerx2)) & (Result_array[Result_i, Result_j]==0)):
#                     Result_array[Result_i, Result_j] = afdx2(DEM_array,i, j,WINDDIRECTION_angle,WINDDIRECTION_theta, MAXHEIGHT)
#                 if ((triggery2 == int(triggery2)) & (Result_array[Result_i, Result_j]==0)):
#                     Result_array[Result_i, Result_j] = afdy2(DEM_array,i, j,WINDDIRECTION_angle,WINDDIRECTION_theta, MAXHEIGHT)
#             del Result_j
#         del Result_i
#     del DEM_array
#     return Result_array


# def cal_Frontal_Area_Density(inRaster, RESOLUTION, lowerLeft, MAXHEIGHT):
#     raster_list=[]
#     # temp_folder = env.scratchWorkspace+ '/temp/'
#     # if not os.path.exists(temp_folder): os.makedirs(temp_folder)
#     # uniqueID = str(time.time_ns())

#     wind_stn_min_dist = None
#     wind_values = None
#     lowerLeft_geometry = arcpy.PointGeometry(lowerLeft, spatial_reference='SVY21.prj')
#     lowerLeft_WGS = lowerLeft_geometry.projectAs('WGS 1984')
#     for wind_stn_id in WIND_DATA:
#         wind_stn = WIND_DATA[wind_stn_id]
#         distanceSq = ((lowerLeft_WGS.firstPoint.X - wind_stn['longitude']) ** 2 
#                   + (lowerLeft_WGS.firstPoint.Y - wind_stn['latitude']) ** 2)
#         if wind_stn_min_dist is None or wind_stn_min_dist > distanceSq:
#             wind_stn_min_dist = distanceSq
#             wind_values = wind_stn['data']

#     Aggregate_RESOLUTION = int(RESOLUTION / inRaster.meanCellHeight)

#     for wind_dir in WIND_DIRECTIONS:
#         print("Processing {0} Direction".format(wind_dir))
#         WINDDIRECTION_angle=wind_values[WIND_DIRECTIONS.index(wind_dir)]
#         WINDDIRECTION_theta=math.radians(WINDDIRECTION_angle)
#         DEM_array=arcpy.RasterToNumPyArray(inRaster,nodata_to_value=0)
#         Result_array=Tile_fad(DEM_array,0,0,WINDDIRECTION_angle,WINDDIRECTION_theta, RESOLUTION, MAXHEIGHT)
#         ResultRaster = arcpy.NumPyArrayToRaster(Result_array,lowerLeft,inRaster.meanCellWidth,inRaster.meanCellHeight)
#         arcpy.DefineProjection_management(ResultRaster, inRaster.spatialReference)
#         # ResultRaster.save(temp_folder+ uniqueID + "_"+str(Layer_index)+"_"+wind_dir+".tif")
#         raster_list.append(ResultRaster)
#         del ResultRaster,Result_array,DEM_array
#         if arcpy.Exists("in_memory"):
#             arcpy.Delete_management("in_memory")
#         gc.collect()
#     arcpy.CheckOutExtension("Spatial")
#     FAD_sum=CellStatistics(raster_list, "MEAN", "NODATA")
#     FADRaster=Aggregate(FAD_sum, Aggregate_RESOLUTION, "MEAN", "EXPAND", "DATA")
#     arcpy.Delete_management(FAD_sum)
#     arcpy.CheckInExtension("Spatial")
#     if arcpy.Exists("in_memory"):arcpy.Delete_management("in_memory")
#     gc.collect()
#     return [FADRaster, raster_list]

