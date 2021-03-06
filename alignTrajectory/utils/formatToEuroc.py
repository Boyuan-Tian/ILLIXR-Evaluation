#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 15:04:26 2020

@author: Boyuan Tian

Transform the pose generated by ILLIXR to Euroc format

	Axis swapped by ILLIXR
	pos_x = -pos_y
	pos_y = pos_z
	pos_z = -pos_x

	quat_w = quat_w
	quat_x = -quat_y
	quat_y = quat_z
	quat_z = -quat_x
"""

import os
import sys


'''
	Read the pose file dumped by ILLIXR
'''
def readFile(folderName, fileName):
	f = open(folderName + fileName)
	lines = f.readlines()
	f.close()

	# lines[1]: timestamp in string format
	timestamp = float(lines[1].strip().split(" ")[1]) / 10**9

	# lines[2]: xyz coordinates
	pos_x = float(lines[2].split(" ")[1])
	pos_y = float(lines[2].split(" ")[2])
	pos_z = float(lines[2].split(" ")[3])

	# lines[3]: quaternion wxyz
	quat_w = float(lines[3].split(" ")[1])
	quat_x = float(lines[3].split(" ")[2])
	quat_y = float(lines[3].split(" ")[3])
	quat_z = float(lines[3].split(" ")[4])

	# return the raw value from file
	# return timestamp, pos_x, pos_y, pos_z, quat_x, quat_y, quat_z, quat_w

	# return the value with unswapped axis
	return timestamp, -pos_z, -pos_x, pos_y, -quat_z, -quat_x, quat_y, quat_w


'''
	Generate the Euroc pose format
	timestamp pos_x pos_y pos_z quat_x quat_y quat_z quat_w
'''
def transformFormat(posePath, startIndex, outputFile):
	poseFileList = os.listdir(posePath)
	poseFileList.remove("metadata.txt")
	poseFileList.sort(key = lambda x:int(x[:-4]))

	# get the timestamp of first frame
	startTimeStamp = readFile(posePath, str(startIndex) + ".txt")[0]

	f = open(outputFile, "w")
	f.write("#timestamp \t pos_x \t pos_y \t pos_z \t quat_x \t quat_y \t quat_z \t quat_w \n")
	for idx, fileName in enumerate(poseFileList):
		if (".txt" in fileName):
			fileIndex = int(fileName.split(".")[0])
			if (fileIndex >= startIndex):
				timestamp, pos_x, pos_y, pos_z, quat_x, quat_y, quat_z, quat_w = readFile(posePath, fileName)

				f.write("%.5f" %(timestamp - startTimeStamp) + " " + \
						"%.7f" %(pos_x) + " " + \
						"%.7f" %(pos_y) + " " + \
						"%.7f" %(pos_z) + " " + \
						"%.7f" %(quat_x) + " " + \
						"%.7f" %(quat_y) + " " + \
						"%.7f" %(quat_z) + " " + \
						"%.7f" %(quat_w) + "\n")
	f.close()


def main():
	if (len(sys.argv) < 4):
		print ("Please setup path and start index to groundtruth and estimated data. ")
		exit("Not enough input arguments !!! ")
	else:
		groundtruthPosePath = sys.argv[1]
		estimatedPosePath = sys.argv[2]
		groundtruthStartIndex = int(sys.argv[3])
		estimatedStartIndex = int(sys.argv[4])

	transformFormat(groundtruthPosePath, groundtruthStartIndex, "./output/groundtruth.txt")
	transformFormat(estimatedPosePath, estimatedStartIndex, "./output/estimated.txt")


if __name__ == '__main__':
	main()