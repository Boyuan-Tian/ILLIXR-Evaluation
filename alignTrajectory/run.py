#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 15:04:26 2020

@author: Boyuan Tian

Description:
	Step1: findStartIndex.py
		- Compute the per-point Euclidean distance between groundtruth and estimated pose.
		- Return the initial frame index.
	Step2: formatToEuroc.py
		- Transform the pose format of ILLIXR data to Euroc format.
		- Transform the timestamp to relative timestamp, both groundtruth and estimated pose.
		- Return two pose files. The frame found in step 1 is the first frame with timestamp 0.
	Step3: alignTrajectory
		- Spatially align the estimated pose to groundtruth.
		- Return the transformation parameters: rotation, translation, quaternion, and scale.
"""

import os

# set path to texture image collected by ILLIXR
groundtruthPosePath = "~/Desktop/OpenXR-Apps/dumped-data/groundtruth/"
estimatedPosePath = "~/Desktop/OpenXR-Apps/dumped-data/estimated/"

# set path and create the folder for intermediate result
tempOutputPath = "./utils/output/"
os.system("rm -rf %s; mkdir -p %s" %(tempOutputPath, tempOutputPath))

'''
	Step1: findStartIndex.py
'''
cmd = "cd ./utils; python findStartIndex.py %s %s" %(groundtruthPosePath, estimatedPosePath)
print (cmd)
if (os.system(cmd)):
	exit("Aborted !!!")


'''
	Ask user to determine the initial frame index and record it
'''
idx_groundtruth = int(input("input first frame index of groundtruth data: "))
idx_estimated = int(input("input first frame index of estimated data: "))

f = open("startIndex.txt", "w")
f.write("groundtruth:\t" + str(idx_groundtruth))
f.write("\n")
f.write("estimated:\t" + str(idx_estimated))
f.close()


'''
	Step2: formatToEuroc.py
'''
cmd = "cd ./utils; python formatToEuroc.py %s %s %d %d" %(groundtruthPosePath, estimatedPosePath, idx_groundtruth, idx_estimated)
print (cmd)
if (os.system(cmd)):
	exit("Aborted !!!")


'''
	Step3: alignTrajectory
'''
cmd = "cd ./utils/align-trajectory/build/; ./alignTrajectory posyaw 0 ../../output/groundtruth.txt ../../output/estimated.txt"
print (cmd)
if (os.system(cmd)):
	exit("Aborted !!!")


print (	"[NEXT STEP]  Please run another round of ILLIXR pose lookup. \n" \
		"[NEXT STEP]  The align matrix will be applied to collect correct texture image.")