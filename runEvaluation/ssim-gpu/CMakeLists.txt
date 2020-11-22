project(ssim-cuda)

cmake_minimum_required(VERSION 2.8 FATAL_ERROR)

# adding required components is essential here for linking !!!
find_package(Boost COMPONENTS system filesystem REQUIRED)
find_package(OpenCV REQUIRED)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -O3 -DNDEBUG")

include_directories("/usr/include/eigen3;/usr/include/boost;/usr/include/python2.7;" include)

add_executable (computeSSIM computeSSIM.cpp)

target_link_libraries (computeSSIM ${Boost_LIBRARIES} ${OpenCV_LIBRARIES} python2.7)

set_property(TARGET computeSSIM PROPERTY CXX_STANDARD 11)