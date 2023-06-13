# #!/opt/local/bin/python2.7
# ##
# ## A python code to calculate AH dispersion 
# ##
# ## Due to SSL certificate problem, this script has to be run with some version of python > 2.7.6
# ##
# ## Written by He Wenhui at FRS, Finished on August 24, 2021

# import arcpy
# from arcpy import env
# from arcpy.sa import *
# from arcpy.ia import *
# import sys
# import json
# import gc
# import time 
# import os

# CWD = os.getcwd()
# RASTER_DEM = CWD + r'\simulations\sky\svf_sg_extent_X.tif'
# RASTER_DEM_DATA=arcpy.Raster(RASTER_DEM)
# MAX_VAL = 255

# def run_sky(bounds):

#     session = str(time.time_ns())
#     env.overwriteOutput = True
#     print('____________________________')

#     data_list=[]
#     data_extent = RASTER_DEM_DATA.extent
#     data_proj = RASTER_DEM_DATA.spatialReference.exportToString()
#     try:
#         # DEM=arcpy.Raster(RASTER_DEM)
#         minmax = [100000, 100000, -100000, -100000]
#         for coords in bounds:
#             minmax[0] = min(minmax[0], coords[0])
#             minmax[1] = min(minmax[1], coords[1])
#             minmax[2] = max(minmax[2], coords[0])
#             minmax[3] = max(minmax[3], coords[1])
#         for i in range(len(minmax)):
#             minmax[i] = str(minmax[i])
#         print('RASTER_DEM_DATA extent', RASTER_DEM_DATA.extent)
#         print('minmax', ' '.join(minmax))
#         # DEM =  arcpy.management.Clip(RASTER_DEM_DATA, minmax, "./temp_result/cut_sky.tif", "#", "#", "NONE")
#         DEM = arcpy.Clip_management(RASTER_DEM, ' '.join(minmax), "./temp_result/cut_sky_" + session + '.tif', "#", "#", "NONE")
#         DEM = arcpy.Raster( "./temp_result/cut_sky_" + session + '.tif')

#         print('DEM.extent', DEM.extent)
#         data_array = arcpy.RasterToNumPyArray( "./temp_result/cut_sky_" + session + '.tif', nodata_to_value=-1)
#         data_list = data_array.tolist()
#         data_extent = str(DEM.extent)
#         data_proj = DEM.spatialReference.exportToString()

#         for i in range(len(data_list)):
#             for j in range(len(data_list[i])):
#                 data_list[i][j] = float(data_list[i][j]) / MAX_VAL
#     except Exception as ex:
#         print('ERROR:', ex)

#     if arcpy.Exists("in_memory"):
#         arcpy.Delete_management("in_memory")
#     arcpy.Delete_management( "./temp_result/cut_sky_" + session + '.tif')
#     gc.collect()

#     # DEM.save("./temp_result/cut.tif")
#     return {
#         "data": data_list,
#         "extent": data_extent,
#         "proj": data_proj,
#         "nodata": -1
#     }
#     # arcpy.CopyRaster_management("./temp_result/cut.tif", "./temp_result/cut.png", nodata_value=0, colormap_to_RGB=True)

#     # arcpy.management.CopyRaster(DEM, "./AH_dispersion_result/cut2.tif")
#     # arcpy.CopyRaster_management(DEM, "./AH_dispersion_result/cut.png")


