cmake_minimum_required(VERSION 3.8)
project(hbts_c)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

# SDK path
set(DHD_SDK_INCLUDE_DIR /home/jiaoyangl/Desktop/sdk-3.17.6-linux-x86_64-gcc/sdk-3.17.6/include)
set(DHD_SDK_LIBRARY_DIR /home/jiaoyangl/Desktop/sdk-3.17.6-linux-x86_64-gcc/sdk-3.17.6/lib/release/lin-x86_64-gcc)

include_directories(${DHD_SDK_INCLUDE_DIR})
link_directories(${DHD_SDK_LIBRARY_DIR})

# Add executable
add_executable(haptic_driver src/haptic_driver.cpp)

# Add dependecies and libs
ament_target_dependencies(haptic_driver rclcpp std_msgs)
target_link_libraries(haptic_driver ${DHD_SDK_LIBRARY_DIR}/libdhd.so.3)

# Install executable
install(TARGETS haptic_driver DESTINATION lib/${PROJECT_NAME})

ament_package()
