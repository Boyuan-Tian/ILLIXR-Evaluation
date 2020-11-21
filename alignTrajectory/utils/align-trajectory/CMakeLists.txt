project(align-trajectory)

cmake_minimum_required(VERSION 2.8 FATAL_ERROR)

# adding required components is essential here for linking !!!
find_package(Boost COMPONENTS system filesystem REQUIRED)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -O3 -DNDEBUG -Wno-deprecated-register -Wno-absolute-value")

include_directories("/usr/include/eigen3;/usr/include/boost;/usr/include/python2.7;" include)

add_executable (alignTrajectory src/AlignTrajectory.cpp src/AlignUtils.cpp src/Loader.cpp src/main.cpp)

target_link_libraries (alignTrajectory ${Boost_LIBRARIES} python2.7)

set_property(TARGET alignTrajectory PROPERTY CXX_STANDARD 11)
