#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 15:04:26 2020

@author: Boyuan Tian

"""

import os
import subprocess

# Set path to texture image here
groundtruthRawPath = "~/Desktop/OpenXR-Apps/dumped-data/groundtruth/"
estimatedRawPath = "~/Desktop/OpenXR-Apps/dumped-data/estimated/"

# No need to change the part below this line in gneral


# Path to write warped image
groundtruthTimewarpPath = "../../../warpedImage/groundtruth/"
estimatedTimewarpPath = "../../../warpedImage/estimated/"

# Folder to store the intermediate result
tempOutputPath = "./utils/output/"

# Prepare folders
os.system("rm -rf %s; mkdir -p %s" %(tempOutputPath, tempOutputPath))


'''
	Step 1: Find the start index of groundtruth and estimated result
'''
cmd = "cd ./utils; python findStartIndex.py %s %s" %(groundtruthRawPath, estimatedRawPath)
print (cmd)

if (os.system(cmd)):
	exit("Aborted !!!")

# Record the start index
idx_groundtruth = int(input("input first frame index of groundtruth data: "))
idx_estimated = int(input("input first frame index of estimated data: "))


f = open("startIndex.txt", "w")
f.write("groundtruth:\t" + str(idx_groundtruth))
f.write("\n")
f.write("estimated:\t" + str(idx_estimated))
f.close()


'''
	Step 2: Generate two data index sequences. The first frame is the reference one with timestamp 0.
'''
cmd = "cd ./utils; python alignTimestamp.py %s %s %d %d" %(groundtruthRawPath, estimatedRawPath, idx_groundtruth, idx_estimated)
print (cmd)

if (os.system(cmd)):
	exit("Aborted !!!")


'''
	Step 3: Compute warped images. Groundtruth and estimated will be computed in parallel.
			Warped images will be written to ./warpedImage/ and consumed by metrices algorithms
'''
# sample command: ./offlineTimewarp <pathToIndexFIle> <pathToRawTextureImage> <pathToOutputImage>
cmd_groundtruth = "cd ./utils/computeTimewarp/build/; ./offlineTimewarp ../../output/groundtruth_index.txt %s %s"\
					 %(groundtruthRawPath, groundtruthTimewarpPath)

os.system(cmd_groundtruth)

cmd_estimated = "cd ./utils/computeTimewarp/build/; ./offlineTimewarp ../../output/estimated_index.txt %s %s"\
					 %(estimatedRawPath, estimatedTimewarpPath)

os.system(cmd_estimated)

# processes = [subprocess.Popen(program, shell=True) for program in [cmd_groundtruth, cmd_estimated]]
# for process in processes:
# 	process.wait()

if (os.system(cmd)):
	exit("Aborted !!!")


'''
	Finish all the processing, move to the next step.
'''
print (	"[NEXT STEP]  Please run an algorithm to evaluate image quality. \n" \
		"[NEXT STEP]  The warped image will be consumed by image similarity assess algorithm.")
