# ILLIXR-Evaluation
## Suggestions and brief explaination:
	1.  Move data, not code. This will minimize the effort to change directories or pass the path as variables in scipts.
		Folder 1: A folder to store evaluation tools, e.g., `~/Desktop/ILLIXR-Evaluation/`
			`git clone git@github.com:Boyuan-Tian/ILLIXR-Evaluation.git`
		Folder 2: A folder to store collected texture data for evaluation, e.g., `~/Desktop/dumped_data/`
		Folder 3: A folder for ILLIXR to write texture data, e.g., `~/Desktop/ILLIXR/output_data/`
			This is the default path but can be changed in config files.

	2.	For each application, there are one round of OpenVINS, and two rounds of pose lookup.
			My observation is that, given the same data sequence, i.e., V1-02, the align matrix for the second round is relative close.
			If we don't have enough time, one alternative way is to run the second round of pose lookup once, and activate macro defination `ALIGN` in pose lookup for other three applications.
			This will not buy us the best result, but my experience is the results are acceptable. I would say do this thing only if we have no time left.

	3.	First round is to get the original pose without alignment. 
			You can turn off the image write in this step for shorter time since the image will not be used, but it requires another build of ILLIXR. Or you can just leave it there.
			Use the pose from first round pose lookup and OpenVINS to compute the align transformation matrix.
		
	4.	Second round will take the align matrix as input to pose lookup, and generate the texture image with correct pose and orientation.


***Following are the steps to run the full experiments for one application:***


## Collect raw texture image
###	A. OpenVINS
		Use monado.yaml. Go to folder: `~/Desktop/ILLIXR/`
		1. Compile ILLIXR runtime.
		2. Set the system environment and activate it. This is the folder 3.
			Need to add ILLIXR_OUTPUT_DATA in .bashrc
		3. Run applications, press q until have enough images or before the memory overfilled. (3600 frames ~ 15 GB)
			Sometimes the OpenVINS will lost tracking and go into somewhere totally wrong.
			At the end of exectution, the program will print time spent on getting texture image for every image.
			If some images take more than 50 ms or even 100 ms to collect image, then we might need to re-run the experiment.
		4. Move the collected data from folder 3 to folder 2, and naming it "estimated".


###	B. Pose lookup
		Use monado-pose-lookup.yaml. Go to folder: `~/Desktop/ILLIXR/`
		Not really sure how does the application load the config file, probably can be assigned somewhere, but I just rename the monado-pose-lookup.yaml to monado.yaml to make it run.
		1. Plugin pose-lookup is preset for the first round. Make sure the macro defination "`ALIGN`" is deactivated (comment out) when running first round pose-lookup.
			If you changed the macro defination settings, remember to re-compile ILLIXR.
		2. Reset the system environment for pose-lookup (add offload_data.so)and activate it.
		3. Run the first round of pose-lookup, press `q` when you have similar number of frames with OpenVINS.
			Optionally, you can comment out the image collection for shorter time, since the texture image here is not going to be used. 
			Turn off the image wrtting requires to build ILLIXR again, so it is ok to just write the image out.
		4. You can set the path in evaluation tool to this data, or you can move the collected data from folder 3 to folder 2, and naming it "groundtruth".

###	C. Align trajectory
		Go to folder: `~/Desktop/ILLIXR-Evaluation/alignTrajectory/`
		1. Set the path in run.py to collected texture images. E.g., path to estimated: `~/Desktop/dumped_data/estimated/`
			If you didn't move the collected data in B.4, set path to groundtruth: `~/Desktop/ILLIXR/output_data/`, otherwise: `~/Desktop/dumped_data/groundtruth/`
		2. `python run.py`
			The first step computes the pair distance for first few hundreds frames in both groundtruth and estimated pose.
			The goal here is to find the matched frames as the beginning point.
			This requires human interleaving and pretty subjective, but the system is robust for not perfect starting frame.
			I will write an algorithm to do this later but have no time for now.
			The frame pair distance are printed reversly. The feature for a good initial pair is:
				Has short pair distance: the distance is in meter, so 0.003 means 3mm. Distance within 5mm is acceptable except very rare case.
				Not far from 0.png: Far away from 0 results in loss too many data. 200 - 500 is ok in general.
				One-on-one match: 155-201, 158-204 is good, but 155-96, 155-97, 155-101 is bad since the 155 is actually not move.
				Stable matching relationship: 155-201, 158-204, 161-207 means groundtruth and estimated data has a stable matching, then any pair is fine as long as they have small distance.
		
		3. Input the index for groundtruth and estimated pose per the guidance, it will compute the align parameters for second round of pose-lookup.
			The script plots aligned trajectories. You can rerun the script if not satisfied with the result.
			The parameters are recorded in `alignMatrix.txt` in the same folder of `run.py`.

###	D. Second round
		Go to folder: `~/Desktop/ILLIXR/`
		1. Open the pose_lookup/plugin.cpp. Activate the macro defination and set the path to alignMatrix.txt.
			You can print the debug information if not sure whether the ALIGN part is executed.
			The path should be a absolute path begin with /home/xxxx. (Not sure the reason yet, but monada has no data when using ~/Desktop/xxx)
		2. Similarlly, you can set the path in evaluation tool if you don't want to move the data.

## Generate Warped Image
###	E. Generate warped image
		Go to folder: `~/Desktop/ILLIXR-Evaluation/offlineTimewarp/`
		1. Set the path in run.py to collected texture images. E.g., path to estimated: `~/Desktop/dumped_data/estimated/`
			If you didn't move the collected data in D.42, set path to groundtruth: `~/Desktop/ILLIXR/output_data/`, otherwise: `~/Desktop/dumped_data/groundtruth/`
		2. `python run.py`
			Similarly, input the index of starting frame for groundtruth and estimated pose seperatelly to temporally align to data sequnence.
			The script will tranfer the absolute timestamp to relative time, and then used by offline timewarp.
			After input index, the script will executes offline timewarp sequentially.
			I tried to use a subprocess in run.py, but the generated image numbers are not always same.
			Execueting the command to genernate warped image in another terminal could save us half of the time, but it the output parameter (last one) need to point to another place.

## Run Image Quality Evaluation
###	F. Compute SSIM
		Go to folder: `~/Desktop/ILLIXR-Evaluation/runEvaluation/`
		1. `python run.py`
			This will computes the SSIM value. Return values include mean, standard deviation, max, and mean.
			Per frame SSIM value will be write to the file ssimScore.txt next to the `run.py`.

## Cleanup
###	G. Cleanup
		Go to folder: `~/Desktop/ILLIXR-Evaluation/`
		1. `python clean.py`
			This will copy the useful experiment result to folder `./RESULT`, and then remove other generated results.
			If you want plot time series, the ssimScore.txt contains per frame information.
			If you want to compute error, the estimted.txt and groundtruth.txt is the aligned pose data in Euroc format. (Only being aligned when you are in the second round)
		2. Copy the `RESULT` folder to another place for future analysis or plotting, and then you can use the same folder for another round of experiment.
			All the generated files will be overwritten by another run of scripts.
