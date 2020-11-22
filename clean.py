#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 15:04:26 2020

@author: Boyuan Tian

"""

import os

# folder to store the intermediate result
tempOutputPath = "./utils/output/"
finalResultPath = "./RESULT/"

# backup the evaluation result
cmd = "mkdir -p %s" %finalResultPath
os.system(cmd)
cmd = "cp ./alignTrajectory/alignMatrix.txt %s" %finalResultPath
os.system(cmd)
cmd = "cp ./alignTrajectory/utils/output/* %s" %finalResultPath
os.system(cmd)
cmd = "cp ./runEvaluation/ssimScore.txt %s" %finalResultPath
os.system(cmd)

# cleanup
cmd = "cd ./alignTrajectory; rm -rf alignMatrix.txt; rm -rf startIndex.txt; rm -rf %s" %tempOutputPath
print (cmd)
if (os.system(cmd)):
	exit("Aborted !!!")

cmd = "cd ./offlineTimewarp; rm -rf warpedImage; rm -rf startIndex.txt; rm -rf %s" %tempOutputPath
print (cmd)
if (os.system(cmd)):
	exit("Aborted !!!")


cmd = "cd ./runEvaluation; rm -rf ssimScore.txt"
print (cmd)
if (os.system(cmd)):
	exit("Aborted !!!")


print (	"[NEXT STEP]  Existing evaluation results are removed. \n" \
		"[NEXT STEP]  Now start another round of evaluation .")