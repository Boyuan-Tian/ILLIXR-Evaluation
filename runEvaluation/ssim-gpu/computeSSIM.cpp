#include <iostream>                   // Console I/O
#include <sstream>                    // String to number conversion
#include <queue>
#include <numeric>
#include <algorithm>

#include <opencv2/core.hpp>      // Basic OpenCV structures
#include <opencv2/core/utility.hpp>
#include <opencv2/imgproc.hpp>// Image processing methods for the CPU
#include <opencv2/imgcodecs.hpp>// Read images

// CUDA structures and methods
#include <opencv2/cudaarithm.hpp>
#include <opencv2/cudafilters.hpp>
#include <boost/filesystem.hpp>

using namespace cv;
using namespace std;
using namespace boost::filesystem;

struct BufferMSSIM                                     // Optimized CUDA versions
{   // Data allocations are very expensive on CUDA. Use a buffer to solve: allocate once reuse later.
	cuda::GpuMat gI1, gI2, gs, t1,t2;

	cuda::GpuMat I1_2, I2_2, I1_I2;
	vector<cuda::GpuMat> vI1, vI2;

	cuda::GpuMat mu1, mu2;
	cuda::GpuMat mu1_2, mu2_2, mu1_mu2;

	cuda::GpuMat sigma1_2, sigma2_2, sigma12;
	cuda::GpuMat t3;

	cuda::GpuMat ssim_map;

	cuda::GpuMat buf;
};

Scalar getMSSIM_CUDA_optimized( const Mat& i1, const Mat& i2, BufferMSSIM& b);

static void help()
{
	cout
		<< "\n--------------------------------------------------------------------------" << endl
		<< "This program shows how to port your CPU code to CUDA or write that from scratch." << endl
		<< "You can see the performance improvement for the similarity check methods (PSNR and SSIM)."  << endl
		<< "Usage:"                                                               << endl
		<< "./gpu-basics-similarity referenceImage comparedImage numberOfTimesToRunTest(like 10)." << endl
		<< "Sample command: ./computeSSIM <path_groundtruth> <path_test> <path_output>"
		<< "--------------------------------------------------------------------------"   << endl
		<< endl;
}

Scalar getMSSIM_CUDA_optimized( const Mat& i1, const Mat& i2, BufferMSSIM& b)
{
	const float C1 = 6.5025f, C2 = 58.5225f;
	/***************************** INITS **********************************/

	b.gI1.upload(i1);
	b.gI2.upload(i2);

	cuda::Stream stream;

	b.gI1.convertTo(b.t1, CV_32F, stream);
	b.gI2.convertTo(b.t2, CV_32F, stream);

	cuda::split(b.t1, b.vI1, stream);
	cuda::split(b.t2, b.vI2, stream);
	Scalar mssim;

	Ptr<cuda::Filter> gauss = cuda::createGaussianFilter(b.vI1[0].type(), -1, Size(11, 11), 1.5);

	for( int i = 0; i < b.gI1.channels(); ++i )
	{
		cuda::multiply(b.vI2[i], b.vI2[i], b.I2_2, 1, -1, stream);        // I2^2
		cuda::multiply(b.vI1[i], b.vI1[i], b.I1_2, 1, -1, stream);        // I1^2
		cuda::multiply(b.vI1[i], b.vI2[i], b.I1_I2, 1, -1, stream);       // I1 * I2

		gauss->apply(b.vI1[i], b.mu1, stream);
		gauss->apply(b.vI2[i], b.mu2, stream);

		cuda::multiply(b.mu1, b.mu1, b.mu1_2, 1, -1, stream);
		cuda::multiply(b.mu2, b.mu2, b.mu2_2, 1, -1, stream);
		cuda::multiply(b.mu1, b.mu2, b.mu1_mu2, 1, -1, stream);

		gauss->apply(b.I1_2, b.sigma1_2, stream);
		cuda::subtract(b.sigma1_2, b.mu1_2, b.sigma1_2, cuda::GpuMat(), -1, stream);
		//b.sigma1_2 -= b.mu1_2;  - This would result in an extra data transfer operation

		gauss->apply(b.I2_2, b.sigma2_2, stream);
		cuda::subtract(b.sigma2_2, b.mu2_2, b.sigma2_2, cuda::GpuMat(), -1, stream);
		//b.sigma2_2 -= b.mu2_2;

		gauss->apply(b.I1_I2, b.sigma12, stream);
		cuda::subtract(b.sigma12, b.mu1_mu2, b.sigma12, cuda::GpuMat(), -1, stream);
		//b.sigma12 -= b.mu1_mu2;

		//here too it would be an extra data transfer due to call of operator*(Scalar, Mat)
		cuda::multiply(b.mu1_mu2, 2, b.t1, 1, -1, stream); //b.t1 = 2 * b.mu1_mu2 + C1;
		cuda::add(b.t1, C1, b.t1, cuda::GpuMat(), -1, stream);
		cuda::multiply(b.sigma12, 2, b.t2, 1, -1, stream); //b.t2 = 2 * b.sigma12 + C2;
		cuda::add(b.t2, C2, b.t2, cuda::GpuMat(), -12, stream);

		cuda::multiply(b.t1, b.t2, b.t3, 1, -1, stream);     // t3 = ((2*mu1_mu2 + C1).*(2*sigma12 + C2))

		cuda::add(b.mu1_2, b.mu2_2, b.t1, cuda::GpuMat(), -1, stream);
		cuda::add(b.t1, C1, b.t1, cuda::GpuMat(), -1, stream);

		cuda::add(b.sigma1_2, b.sigma2_2, b.t2, cuda::GpuMat(), -1, stream);
		cuda::add(b.t2, C2, b.t2, cuda::GpuMat(), -1, stream);


		cuda::multiply(b.t1, b.t2, b.t1, 1, -1, stream);     // t1 =((mu1_2 + mu2_2 + C1).*(sigma1_2 + sigma2_2 + C2))
		cuda::divide(b.t3, b.t1, b.ssim_map, 1, -1, stream);      // ssim_map =  t3./t1;

		stream.waitForCompletion();

		Scalar s = cuda::sum(b.ssim_map, b.buf);
		mssim.val[i] = s.val[0] / (b.ssim_map.rows * b.ssim_map.cols);

	}
	return mssim;
}


static bool comp(std::string x, std::string y)
{
	std::string::size_type pos;

	pos = x.find(".");
	int x_idx = std::stoi(x.substr(0, pos));

	pos = y.find(".");
	int y_idx = std::stoi(y.substr(0, pos));

	return x_idx < y_idx;
}


int main(int argc, char *argv[])
{
	help();

	string groudtruth_dir;
	string test_dir;
	string output_dir;

	double score;
	std::vector<double> ssim_score;

	if (argc == 4)
	{
		groudtruth_dir = argv[1];
		test_dir = argv[2];
		output_dir = argv[3];
	}
	else
	{
		std::cout << "Mismatch input arguments, use the default one !!!" << std::endl;

		groudtruth_dir = "/home/power-rdx/Desktop/Evaluate-Toolchain/bin/step3_offlineTimewarp/aligned_pose_lookup/";
		test_dir = "/home/power-rdx/Desktop/Evaluate-Toolchain/bin/step3_offlineTimewarp/openvins/";
		output_dir = "./";
	}

	Scalar x;
	double time = 0;
	path p(groudtruth_dir);
	std::vector<std::string> fileNameList;

	// get file names of the target directory
	for (auto i = directory_iterator(p); i != directory_iterator(); i++)
	{
		if (!is_directory(i->path()))
		{
			string filename = i->path().filename().string();
			fileNameList.push_back(filename);
		}
	}

	// sort the image
	std::sort(fileNameList.begin(),fileNameList.end(), comp);

	for (int i = 0; i < fileNameList.size(); i++)
	{
		std::cout << "========================  " << i << " / " << fileNameList.size() << "  ========================" << endl;
		string filename = fileNameList[i];

		Mat I1 = imread(groudtruth_dir + filename);           // Read the two images
		Mat I2 = imread(test_dir + filename);

		if (!I1.data || !I2.data)           // Check for success
		{
			cout << "Couldn't read the image";
			return 0;
		}

		BufferMSSIM bufferMSSIM;


		//------------------------------- SSIM CUDA Optimized--------------------------------------------
		time = (double)getTickCount();

		cvtColor(I1, I1, CV_BGR2GRAY);
		cvtColor(I2, I2, CV_BGR2GRAY);

		x = getMSSIM_CUDA_optimized(I1,I2, bufferMSSIM);

		time = 1000*((double)getTickCount() - time)/getTickFrequency();

		std::cout << "Time: " << time << " ms" << "\t" << \
					 "Accuracy:" << " B" << x.val[0] << " G" << x.val[1] << " R" << x.val[2] << std::endl;

		ssim_score.push_back(sum(x)[0]);
	}


	double mean = std::accumulate(ssim_score.begin(), ssim_score.end(), 0.0) / ssim_score.size();
	cout << "mean: " << mean << endl;

	double accum = 0.0;
	std::for_each(std::begin(ssim_score), std::end(ssim_score), [&](const double d){
		accum += (d - mean) * (d - mean);
	});
	
	double stdev = sqrt(accum/(ssim_score.size() - 1));
	std::cout << "std: " << stdev << std::endl;

	std::vector<double>::iterator max = std::max_element(ssim_score.begin(), ssim_score.end());
	std::vector<double>::iterator min = std::min_element(ssim_score.begin(), ssim_score.end());
	std::cout << "max: " << *max << " min: " << *min << std::endl;

	std::string fileName = output_dir + "ssimScore.txt";
	std::ofstream output (fileName);
	if (output.is_open())
	{
		output << "SSIM Result" << std::endl; 
		output << "mean: " << mean << std::endl;
		output << "max: " << *max << std::endl;
		output << "min: " << *min << std::endl;
		output << "stdev: " << stdev << std::endl;
		output << "total number: " << ssim_score.size() << std::endl;

		output << "ssim score: " << std::endl;
		output << "index \t score" << std::endl;
		for (int i = 0; i < ssim_score.size(); i++)
				output << i << "\t" << ssim_score[i] << std::endl;
	}
	output.close();

	return 0;
}