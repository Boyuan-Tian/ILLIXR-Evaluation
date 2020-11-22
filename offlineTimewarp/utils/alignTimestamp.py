#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 9 15:25:22 2020

@author: Boyuan Tian

Align the timestamp of groundtruth and estimated pose
"""

import os
import sys


'''
	Read the pose time dumped by ILLIXR
'''
def readFile(folderName, fileName):
	f = open(folderName + fileName)
	lines = f.readlines()
	f.close()
	
	fileTime = int(lines[1].split(": ")[1].split("\n")[0])
	return fileTime
	

'''
	Find the cloest target given a query data and a search list
'''
def findClosest(query, targetList):
	diffFunction = lambda listValue : abs(listValue - query)
	closestValue = min(targetList, key = diffFunction)
	return closestValue


'''
	Compute the relative time to the first frame
'''
def computeDiffList(posePath, startIndex):
	poseFileList = os.listdir(posePath)
	poseFileList.remove("metadata.txt")
	poseFileList.sort(key = lambda x:int(x[:-4]))

	startTime = readFile(posePath, str(startIndex) + ".txt")

	diff_list = []
	for idx, data in enumerate(poseFileList):
		if (int(data.split(".")[0]) >= startIndex) and ("txt" in data):
			fileTime = readFile(posePath, data)
			diff_list.append(fileTime - startTime)
	return diff_list


def main():
	if (len(sys.argv) < 4):
		print ("Please setup path and start index to groundtruth and estimated data. ")
		exit("Not enough input arguments !!! ")
	else:
		groundtruthPosePath = sys.argv[1]
		estimatedPosePath = sys.argv[2]
		groundtruthStartIndex = int(sys.argv[3])
		estimatedStartIndex = int(sys.argv[4])

	diff_groundtruth = computeDiffList(groundtruthPosePath, groundtruthStartIndex)
	diff_estimated = computeDiffList(estimatedPosePath, estimatedStartIndex)

	estimated_final_index = []
	groundtruth_final_index = []

	for idx, data in enumerate(diff_estimated):
		closest_value = findClosest(data, diff_groundtruth)

		local_idx = diff_estimated.index(data)
		estimated_final_index.append(local_idx + estimatedStartIndex)
		
		local_idx = diff_groundtruth.index(closest_value)
		groundtruth_final_index.append(local_idx + groundtruthStartIndex)

		# if estimated poses are less than groundtruth, we are good
		# if groundtruth less than estimated poses, cut off the estimated data here
		if closest_value == diff_groundtruth[-1]:
			break

	# write out the index list which is temporally aligned
	f = open("./output/groundtruth_index.txt", "w")
	for idx, data in enumerate(groundtruth_final_index):
		f.write(str(data) + "\n")
	f.close() 

	f = open("./output/estimated_index.txt", "w")
	for idx, data in enumerate(estimated_final_index):
		f.write(str(data) + "\n")
	f.close()


if __name__ == '__main__':
	main()