cmake_minimum_required(VERSION 3.10)

project(rextr)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "-Wno-deprecated-declarations")
set(CMAKE_BUILD_TYPE Debug)

find_package(OpenSSL REQUIRED)
include_directories(${OPENSSL_INCLUDE_DIR})

set(MAIN_SRC cpp-src/rextr.cpp)

file(GLOB ENC_SRCS          "cpp-src/enc/*.cpp")
file(GLOB EXTR_SRCS         "cpp-src/extr/*.cpp")
file(GLOB REPACK_SRCS       "cpp-src/repack/*.cpp")
file(GLOB SPECIAL_SRCS      "cpp-src/special/*.cpp")
file(GLOB STRUCTURE_SRCS    "cpp-src/structure/*.cpp")
file(GLOB UTILS_SRCS        "cpp-src/utils/*.cpp")

set(PROJECT_SRCS
    ${MAIN_SRC}
    ${ENC_SRCS}
    ${EXTR_SRCS}
    ${REPACK_SRCS}
    ${SPECIAL_SRCS}
    ${STRUCTURE_SRCS}
    ${UTILS_SRCS}
)

add_executable(
    rextr 
    ${PROJECT_SRCS}
)

target_include_directories(
    rextr 
PUBLIC 
    cpp-src/enc
    cpp-src/extr
    cpp-src/repack
    cpp-src/speical
    cpp-src/utils
    cpp-src
)

target_link_libraries(
    rextr 
PRIVATE
    ${OPENSSL_LIBRARIES}
)