cmake_minimum_required(VERSION 3.10)
project(hailo_anpr_postprocess)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(PkgConfig REQUIRED)
pkg_check_modules(GSTREAMER REQUIRED gstreamer-1.0)
pkg_check_modules(HAILO REQUIRED hailo)

# Include directories
include_directories(
    ${GSTREAMER_INCLUDE_DIRS}
    ${HAILO_INCLUDE_DIRS}
    ${CMAKE_CURRENT_SOURCE_DIR}
)

# Link directories
link_directories(
    ${GSTREAMER_LIBRARY_DIRS}
    ${HAILO_LIBRARY_DIRS}
)

# Plate Detection Plugin
add_library(plate_detection SHARED plate_detection.cpp)
target_link_libraries(plate_detection
    ${GSTREAMER_LIBRARIES}
    ${HAILO_LIBRARIES}
)

# Plate OCR Plugin
add_library(plate_ocr SHARED plate_ocr.cpp)
target_link_libraries(plate_ocr
    ${GSTREAMER_LIBRARIES}
    ${HAILO_LIBRARIES}
)

# Plate Cropper Plugin (placeholder - implement as needed)
add_library(plate_crop SHARED plate_crop.cpp)
target_link_libraries(plate_crop
    ${GSTREAMER_LIBRARIES}
    ${HAILO_LIBRARIES}
)

# Install libraries
install(TARGETS plate_detection plate_ocr plate_crop
    LIBRARY DESTINATION /usr/local/lib/gstreamer-1.0
)
