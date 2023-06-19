# import arcpy
# from arcpy import env
# from arcpy.sa import *
# from arcpy.ia import *
# import sys
# import json
# import gc
# import time 
# import os

# from .clip_shp_features import clip_shp_features, clip_feature_bound

# CWD = os.getcwd()
# SHP_FILE= CWD + r'\simulations\shp\singapore_building_SVY.shp'
# SPATIAL_REF = arcpy.Describe(SHP_FILE)
# CLIP_DISTANCE = 200.0 / 111139

# def geojson_to_feature(session, data, sim_bound, feat_bound):
#     clipped_shp = clip_shp_features(session, sim_bound)
#     buildings_shp = clip_feature_bound(session, clipped_shp, feat_bound)

#     geojson_file = CWD + "/temp_result/geojson_" + session + '.geojson'

#     f = open(geojson_file, "w")
#     f.write(str(data))
#     f.close()

#     uploaded_features = CWD + "/temp_result/json_" + session + '.shp'
#     arcpy.JSONToFeatures_conversion(geojson_file, uploaded_features)
#     merged_file = CWD + "/temp_result/merged_" + session + '.shp'
#     arcpy.Merge_management([buildings_shp, uploaded_features], merged_file)
#     output_raster = CWD + "/temp_result/uploaded_" + session + '.tif'
#     arcpy.FeatureToRaster_conversion(merged_file, "AGL", output_raster, 1)

#     arcpy.Delete_management(clipped_shp)
#     arcpy.Delete_management(buildings_shp)
#     arcpy.Delete_management(uploaded_features)
#     arcpy.Delete_management(merged_file)
#     os.remove(geojson_file)
#     if arcpy.Exists("in_memory"):arcpy.Delete_management("in_memory")
#     return output_raster
