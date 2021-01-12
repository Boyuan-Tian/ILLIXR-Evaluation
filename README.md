# ILLIXR-Evaluation
## Suggestions and a brief explanation:
1. Move data, not code. This will minimize the effort to change directories or pass the path as variables in scripts. <br>
	- Folder 1: A folder to store evaluation tools, e.g., `~/Desktop/ILLIXR-Evaluation/` <br>
	```
	$ git clone git@github.com:Boyuan-Tian/ILLIXR-Evaluation.git
	```
	- Folder 2: A folder to store collected texture data for evaluation, e.g., `~/Desktop/dumped_data/` <br>
	- Folder 3: A folder for ILLIXR to write texture data, e.g., `~/Desktop/ILLIXR/output_data/` <br>
		- This is the default path but can be changed in config files.

2. For each application, there is one round of OpenVINS, and two rounds of pose lookup. <br>
	- My observation is that, given the same data sequence, i.e., V1-02, the align matrix for the second round is relatively close.
	- If we don't have enough time, one alternative way is to run the second round of pose lookup once, and activate macro definition `ALIGN` in pose lookup for the other three applications.
	- This will not buy us the best result, but my experience is the results are acceptable. I would say do this thing only if we have no time left.

3. First round is to get the original pose without alignment. 
	- You can turn off image writing in this step for a shorter time since the image will not be used, but it requires another build of ILLIXR. Or you can just leave it there.
	- Use the pose from the first-round pose lookup and OpenVINS to compute the align transformation matrix.
		
4. Second round will take the align matrix as input to pose lookup and generate the texture image with correct pose and orientation.


***Following are the steps to run the full experiments for one application:***


## Collect raw texture image
###	A. OpenVINS
***Use monado.yaml. Go to folder: `~/Desktop/ILLIXR/`***
1. Compile ILLIXR runtime.
2. Set the system environment and activate it. This is the folder 3.
	- Need to add ILLIXR_OUTPUT_DATA in .bashrc
3. Run applications, press `q` until having enough images or before the memory is overfilled. (3600 frames ~ 15 GB)
	- Sometimes the OpenVINS will lose tracking and go somewhere totally wrong.
	- At the end of execution, the program will print time spent on getting texture images for every image.
	- If some images take more than 50 ms or even 100 ms to collect the image, then we might need to re-run the experiment.
4. Move the collected data from folder 3 to folder 2, and naming it "estimated".


###	B. Pose lookup
***Use monado-pose-lookup.yaml. Go to folder: `~/Desktop/ILLIXR/`***
```
Not sure how does the application load the config file, probably can be assigned somewhere, but I just rename the monado-pose-lookup.yaml to monado.yaml to make it run.
```
1. Plugin pose-lookup is preset for the first round. Make sure the macro definition "`ALIGN`" is deactivated (comment out) when running the first round pose-lookup.
	- If you changed the macro definition settings, remember to re-compile ILLIXR.
2. Reset the system environment for pose-lookup (add offload_data.so)and activate it.
3. Run the first round of pose-lookup, press `q` when you have a similar number of frames with OpenVINS.
	- Optionally, you can comment out the image collection for shorter time, since the texture image here is not going to be used. 
	- Turn off the image wrtting requires to build ILLIXR again, so it is ok to just write the image out.
4. You can set the path in evaluation tool to this data, or you can move the collected data from folder 3 to folder 2, and naming it "groundtruth".

###	C. Align trajectory
***Go to folder: `~/Desktop/ILLIXR-Evaluation/alignTrajectory/`***
1. Set the path in run.py to collected texture images. E.g., path to estimated: `~/Desktop/dumped_data/estimated/`
	- If you didn't move the collected data in B.4, set path to groundtruth: `~/Desktop/ILLIXR/output_data/`, otherwise: `~/Desktop/dumped_data/groundtruth/`
2. `python run.py`
	- The first step computes the pair distance for first few hundreds of frames in both groundtruth and estimated pose.
	- The goal here is to find the matched frames as the beginning point.
	- This requires human interleaving and pretty subjective, but the system is robust for not perfect starting frame.
	- I will write an algorithm to do this later but have no time for now.
	- The frame pair distance are printed reversely. The feature for a good initial pair is:
		- Has short pair distance: the distance is in meter, so 0.003 means 3mm. Distance within 5mm is acceptable except in a very rare case.
		- Not far from 0.png: Far away from 0 results in the loss of many data. 200 - 500 is ok in general.
		- One-on-one match: 155-201, 158-204 is good, but 155-96, 155-97, 155-101 is bad since the 155 is not moving.
		- Stable matching relationship: 155-201, 158-204, 161-207 means groundtruth and estimated data have a stable matching, then any pair is fine as long as they have a small distance.
		
3. Input the index for groundtruth and estimated pose per the guidance, it will compute the align parameters for the second round of pose-lookup.
	- The script plots aligned trajectories. You can rerun the script if not satisfied with the result.
	- The parameters are recorded in `alignMatrix.txt` in the same folder of `run.py`.

###	D. Second round
***Go to folder: `~/Desktop/ILLIXR/`***
1. Open the pose_lookup/plugin.cpp. Activate the macro definition and set the path to alignMatrix.txt.
	- You can print the debug information if not sure whether the ALIGN part is executed.
	- The path should be absolute beginning with /home/xxxx. (Not sure the reason yet, but Monado has no data when using ~/Desktop/xxx)
2. Similarly, you can set the path in the evaluation tool if you don't want to move the data.

## Generate Warped Image
###	E. Generate warped image
***Go to folder: `~/Desktop/ILLIXR-Evaluation/offlineTimewarp/`***
1. Set the path in run.py to collected texture images. E.g., path to estimated: `~/Desktop/dumped_data/estimated/`
	- If you didn't move the collected data in D.42, set path to groundtruth: `~/Desktop/ILLIXR/output_data/`, otherwise: `~/Desktop/dumped_data/groundtruth/`
2. `python run.py`
	- Similarly, input the index of the starting frame for groundtruth and estimated pose separately to temporally align to the data sequence.
	- The script will transfer the absolute timestamp to relative time and then be used by offline timewarp.
	- After the input index, the script will execute offline timewarp sequentially.
	- I tried to use a subprocess in run.py, but the generated image numbers are not always the same.
	- Executing the command to generate a warped image in another terminal could save us half of the time, but the output parameter (last one) needs to point to another place.
3. Check the folder `~/Desktop/ILLIXR-Evaluatin/offlineTimewarp/warpedImage`
	- Make sure the folder `groundtruth` and `estimated` have the same number of images, otherwise the SSIM algorithm will raise an error.

## Run Image Quality Evaluation
###	F. Compute SSIM
***Go to folder: `~/Desktop/ILLIXR-Evaluation/runEvaluation/`***
1. `python run.py`
	- This will computes the SSIM value. Return values include mean, standard deviation, max, and mean.
	- Per frame SSIM value will be written to the file ssimScore.txt next to the `run.py`.

## Cleanup
###	G. Cleanup
***Go to folder: `~/Desktop/ILLIXR-Evaluation/`***
1. `python clean.py`
	- This will copy the useful experiment result to folder `./RESULT`, and then remove other generated results.
	- If you want plot time series, the ssimScore.txt contains per frame information.
	- If you want to compute error, the estimted.txt and groundtruth.txt are the aligned pose data in Euroc format. (Only being aligned when you are in the second round)
2. Copy the `RESULT` folder to another place for future analysis or plotting, and then you can use the same folder for another round of the experiment.
	- All the generated files will be overwritten by another run of scripts.
