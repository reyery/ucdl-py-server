import arcpy
from arcpy import env
from arcpy.sa import *
import math
import time
import numpy
import gc
import sys
import os

MaxRange=100

def FA(m,n):
    fa=0
    for i in range(m-MaxRange,m+MaxRange+1):
        fa2=0
        for j in range(n-MaxRange,n+MaxRange+1):
            if (i>=0) and (j<DEM_width) and (j>=0) and (i<DEM_height):
                delta1=abs(m-i)
                delta2=abs(n-j)
                D=math.sqrt((delta1*delta1)+(delta2*delta2))
                if D<100:
                    fa1=DEM_array[i,j]*(MaxRange-D)/MaxRange
                    fa2=fa2+fa1
        fa=fa+fa2
    print ("m: "+str(m) +"  n:  "+str(n))
    return fa


#onedrive_path=r"C:\Users\hwh\Yuan Chao's Lab Dropbox\wenhui he"
onedrive_path=r"C:\Users\akihw\Yuan Chao's Lab Dropbox\wenhui he"
env.workspace=onedrive_path+"/SLA_data/sample_data/"
env.scratchWorkspace =onedrive_path+"/FAD/fa_radius_result/"
arcpy.CheckOutExtension("Spatial")
DEM=arcpy.Raster(r"C:\Users\akihw\Yuan Chao's Lab Dropbox\wenhui he\SLA_data\sample_data\SLA_DEM_temp_cut_new.tif")
DEM_width=DEM.width
DEM_height=DEM.height
print (DEM_width,DEM_height)
lowerLeft = arcpy.Point(DEM.extent.XMin, DEM.extent.YMin)
Result_array=numpy.zeros((DEM_height,DEM_width))
DEM_array=arcpy.RasterToNumPyArray(DEM,nodata_to_value=0)
print (DEM_array.shape)
for i in range(0,DEM_height): # notice that i is from top
    for j in range(0,DEM_width):
        Result_array[i, j]=FA(i,j)
ResultRaster = arcpy.NumPyArrayToRaster(Result_array,lowerLeft,x_cell_size=1)
ResultRaster.save(env.scratchWorkspace+"/FA2.tif")
