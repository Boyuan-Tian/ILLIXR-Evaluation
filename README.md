# ILLIXR-Evaluation
## About:
1. To minimize the changing of directories in the evaluation, we choose to move the data instead of the code. <br>
	There are three folders for evaluation.
	- Folder 1: A folder to store evaluation tools (this repo), e.g., `~/Desktop/ILLIXR-Evaluation/` <br>
	```
	$ git clone git@github.com:Boyuan-Tian/ILLIXR-Evaluation.git
	```
	- Folder 2: A folder to store collected texture data, e.g., `~/Desktop/dumped_data/` <br>
	- Folder 3: A folder to write texture data when executing the ILLIXR runtime, e.g., `~/Desktop/ILLIXR/output_data/` <br>
		- This is the default path but can be changed in config files.

2. For each application, there is one round of OpenVINS (estimated pose) and two rounds of pose-lookup (ground truth).
	- The round of OpenVINS produces estimated poses. 
	- First round of pose-lookup gets the original pose used for alignment and outputs a text file with the align matrix.
	- Second round of pose-lookup takes the align matrix and generates the texture images in the correct position and orientation.

3. Tips to save execution time.
	- Image writing in the first round of pose-lookup can be skipped, as the collected texture images will be ignored.
	- The entire alignment can be skipped if the evaluation runs on the same data sequence but with different applications.


***Following are the steps to run the full experiments for one application:***


## Collect raw texture image
###	A. OpenVINS
***Use monado.yaml. Go to folder: `~/Desktop/ILLIXR/`***
1. Compile the ILLIXR runtime.
	```
	$ ./runner.sh configs/monado.yaml
	```
2. Add the directory of `folder 3` to the system environment and activate it.
	- Open `.bashrc`, add the following line to the end of the file.
	```
		export ILLIXR_OUTPUT_DATA = $path-to-ILLIXR$/output_data/
	```
	- Activate the environment by `source ~/.bashrc`.

3. Run ILLIXE until having enough images or before the memory overflowed. (3600 frames ~ 15 GB).
	- Sometimes OpenVINS may lose tracking and go somewhere totally wrong. Please try to run the program one more time.
	- The metadata about texture image collection will be recorded and printed at the end of execution.
	- An image that takes >= 70 ms or 100 ms to collect means somewhere bottlenecked, it would be safe to run the experiment again.
4. Move the collected data from `folder 3` to `folder 2`, and naming it `estimated`.


###	B. Pose-lookup
***Use monado-pose-lookup.yaml. Go to folder: `~/Desktop/ILLIXR/`***
1. Plugin pose-lookup is pre-set for the first round. Make sure the macro definition `ALIGN` is deactivated (comment out) when running the first round pose-lookup.
	- If you changed the macro definition settings, remember to re-compile ILLIXR.
2. Reset the system environment for pose-lookup (add offload_data.so if running OpenXR Apps) and activate it.
3. Run the first round of pose-lookup until there is a similar number of frames with OpenVINS.
	- Optionally, you can turn off the image collection to save time, as the texture images will be ignored. 
	- Noting that turn off the image writing requires to build ILLIXR again.
4. It is recommended to set the path to the collected data in evaluation scripts, but you can also move the data from `folder 3` to `folder 2`, and naming it `groundtruth`.

###	C. Align trajectory
***Go to folder: `~/Desktop/ILLIXR-Evaluation/alignTrajectory/`***
1. Set the path in `run.py` for collected texture images. 
	- E.g., path to estimated data: `~/Desktop/dumped_data/estimated/`
	- If you didn't move the collected data in B.4, set path for groundtruth: `~/Desktop/ILLIXR/output_data/`. <br>
	Otherwise: `~/Desktop/dumped_data/groundtruth/`
2. Run the script for trajectory alignment.
	```
	$ python run.py
	```
	- The script first aligns the beginning frames between ground truth and estimated poses. It computes and sorts the pair distance for the first few hundreds of frames in both data sequences.
	- The pair distances are printed reversely, and the user is asked to input the frame index of ground truth and estimated data.
	- Following are the features of a good initial pair:
		- Short distance: Distance within 5mm (0.005) is preferable except in some very rare cases.
		- Close to 0.png: Far away from 0 results in the skipping of too many frames. 200 - 500 is preferable in general.
		- One-on-one match: 155-201, 158-204 is good, but 155-96, 155-97, 155-101 is bad since the frame 155 may not be moving.
		- Stable matching relationship: 155-201, 156-202, 168-204 means there is a stable matching, then any pair can be picked as long as the distance is short enough.
		
3. The align parameters for the second round of pose-lookup will be computed after put in the index pair of initial frames.
	- The script plots aligned trajectories. You can rerun the script with a different pair of initial frames if not satisfied with the result.
	- The parameters are written to `alignMatrix.txt` in the same folder of `run.py`.

###	D. Second round
***Go to folder: `~/Desktop/ILLIXR/`***
1. Open the `pose_lookup/plugin.cpp`. Activate the macro definition `ALIGN` and set the path to `alignMatrix.txt`.
	- Please use the absolute path to referring to the `alignMatrix.txt`
2. Run ILLIXR with pose-lookup again to collect the aligned texture images.
	- Similarly, the path can be set in the evaluation script if the data is not moved after collection.

## Generate Warped Image
###	E. Generate warped image
***Go to folder: `~/Desktop/ILLIXR-Evaluation/offlineTimewarp/`***
1. Set the path in `run.py` for collected texture images.
	- E.g., path to estimated data: `~/Desktop/dumped_data/estimated/`
	- If you didn't move the collected data in B.4, set path for groundtruth: `~/Desktop/ILLIXR/output_data/`. <br>
	Otherwise: `~/Desktop/dumped_data/groundtruth/`
2. Run the script for offline timewarp.
	```
	$ python run.py
	```
	- Similarly, input the index of the starting frame for ground truth and estimated poses to align two data sequences.
	- The script will transfer the absolute timestamp to relative time and then produce the warped images.
3. Check the folder `~/Desktop/ILLIXR-Evaluatin/offlineTimewarp/warpedImage`
	- Make sure the folder `groundtruth` and `estimated` have the same number of images, otherwise the image quality assessment will raise an error.

## Run Image Quality Evaluation
###	F. Compute SSIM/FILP score
***Go to folder: `~/Desktop/ILLIXR-Evaluation/runEvaluation/`***
1. Run the script for image quality evaluation.
	```
	#$ python run.py --metrics#
	```
	- The script computes a variety of image quality metrics, and we currently support the computation for SSIM and Nvidia FILP. The return outputs include mean, standard deviation, max, and min.
	- Evaluation result for each frame will be written to a text file in the same directory.

## Cleanup
###	G. Cleanup
***Go to folder: `~/Desktop/ILLIXR-Evaluation/`***
1. Run the script for clean up.
	```
	$ python run.py
	```
	- This script copies the experiment results to folder `./RESULT` and then removes all other intermediate files.
	- If you want plot time series, the ssimScore.txt contains per-frame information.
	- If you want to compute trajectory error, the estimted.txt and groundtruth.txt are the aligned pose data in EUROC format.
2. Copy the folder `RESULT` to somewhere else for future analysis, and then the same folder can be used for another round of the experiment.
	- ***All the files generated in the evaluation will be overwritten by another run of scripts.***
