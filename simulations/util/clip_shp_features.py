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
# SHP_FILE= CWD + r'\simulations\shp\singapore_building_SVY.shp'
# SPATIAL_REF = arcpy.Describe(SHP_FILE)
# CLIP_DISTANCE = 200.0 / 111139

# def clip_shp_features(session, clip_bounds):
#     env.overwriteOutput = True
#     minmax = [10000000, 10000000, -10000000, -10000000]
#     for coords in clip_bounds:
#         minmax[0] = min(minmax[0], coords[0])
#         minmax[1] = min(minmax[1], coords[1])
#         minmax[2] = max(minmax[2], coords[0])
#         minmax[3] = max(minmax[3], coords[1])
#     minmax[0] -= CLIP_DISTANCE
#     minmax[1] -= CLIP_DISTANCE
#     minmax[2] += CLIP_DISTANCE
#     minmax[3] += CLIP_DISTANCE
#     polygonPts = arcpy.Array([
#         arcpy.Point(minmax[0], minmax[1]),
#         arcpy.Point(minmax[2], minmax[1]),
#         arcpy.Point(minmax[2], minmax[3]),
#         arcpy.Point(minmax[0], minmax[3]),
#         arcpy.Point(minmax[0], minmax[1])
#     ])
#     pg = arcpy.Polygon(polygonPts, arcpy.SpatialReference(4326))

#     out_features = CWD + "/temp_result/clip1_" + session + '.shp'
#     arcpy.Clip_analysis(SHP_FILE, pg, out_features)
#     return out_features

# def clip_feature_bound(session, in_features, clip_bounds):
#     env.overwriteOutput = True
#     coords = []
#     for coord in clip_bounds:
#         coords.append(arcpy.Point(coord[0], coord[1]))
#     coords.append(coords[0])
#     pg = arcpy.Polygon(arcpy.Array(coords), arcpy.SpatialReference(4326))
#     out_features = CWD + "/temp_result/clip2_" + session + '.shp'
#     selection = arcpy.SelectLayerByLocation_management(in_features, 'INTERSECT', pg)
#     arcpy.DeleteFeatures_management(selection)
#     arcpy.CopyFeatures_management(in_features, out_features)
#     return out_features