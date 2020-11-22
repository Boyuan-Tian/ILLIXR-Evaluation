#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 15:04:26 2020

@author: Boyuan Tian

"""

import os

# set path to warped image here
groundtruthTimewarpPath = "../../../offlineTimewarp/warpedImage/groundtruth/"
estimatedTimewarpPath = "../../../offlineTimewarp/warpedImage/estimated/"
outputPath = "../../"

cmd = "cd ./ssim-gpu/build; ./computeSSIM %s %s %s" %(groundtruthTimewarpPath, estimatedTimewarpPath, outputPath)
print (cmd)

if (os.system(cmd)):
	exit("Aborted !!!")

print (	"[NEXT STEP]  Please run an algorithm to evaluate image quality. \n" \
		"[NEXT STEP]  The warped image will be consumed by image similarity assess algorithm.")