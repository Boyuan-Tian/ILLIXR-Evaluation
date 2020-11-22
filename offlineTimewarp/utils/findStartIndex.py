#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 8 03:24:15 2020

@author: Boyuan Tian

Find the index of initial frame
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
	
	# lines[2] stores xyz coordinates
	x = float(lines[2].split(" ")[1])
	y = float(lines[2].split(" ")[2])
	z = float(lines[2].split(" ")[3])
	return x, y, z


'''
	Compute Euclidean distance between two points
'''
def computeDistance(x_est, y_est, z_est, x_gt, y_gt, z_gt):
	distance = (x_est - x_gt)**2 + (y_est - y_gt)**2 + (z_est - z_gt)**2
	return distance


def main():
	print ("Computing the index of starting frame ... ")

	if (len(sys.argv) < 2):
		print ("Please setup path to groundtruth and estimated data. ")
		exit("Not enough input arguments !!! ")
	else:
		groundTruthPath = sys.argv[1]
		estimatedPath = sys.argv[2]

	groundTruthList = os.listdir(groundTruthPath)
	groundTruthList.remove("metadata.txt")
	groundTruthList.sort(key = lambda x:int(x[:-4]))

	estimatedList = os.listdir(estimatedPath)
	estimatedList.remove("metadata.txt")
	estimatedList.sort(key = lambda x:int(x[:-4]))

	pair_distance = {}

	# search range for estimated pose
	for idx_est, data_est in enumerate(estimatedList[:1000]):
		if ("txt" in data_est):
			min_distance = 10000.0
			key_min_distance = "N/A"

			x_est, y_est, z_est = readFile(estimatedPath, data_est)

			# search range for groundtruth pose
			for idx_gt, data_gt in enumerate(groundTruthList[300:1000]):
				if ("txt" in data_gt):
					x_gt, y_gt, z_gt = readFile(groundTruthPath, data_gt)
					distance = computeDistance(x_est, y_est, z_est, x_gt, y_gt, z_gt)

					if distance < min_distance:
						min_distance = distance
						key_min_distance = str(data_gt) + "  ---  " +  str(data_est)

			pair_distance[key_min_distance] = min_distance


	# get the key for value with minimal value
	# min_key = list(pair_distance.keys())[list(pair_distance.values()).index(min(list(pair_distance.values())))]

	pair_distance = (sorted(pair_distance.items(), key = lambda kv:(kv[1], kv[0])))

	f = open("./output/pair_distance.txt", "w")
	for idx, data in enumerate(pair_distance):
		f.write(str(data) + "\n")
	f.close()

	# gt --- est
	pair_distance.reverse()
	for idx, data in enumerate(pair_distance):
		print ("groundtruth --- estimated: ", data)


if __name__ == '__main__':
	main()