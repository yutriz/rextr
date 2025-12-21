cmake_minimum_required(VERSION 3.10)

project(rextr)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "-Wno-deprecated-declarations")

find_package(OpenSSL REQUIRED)
include_directories(${OPENSSL_INCLUDE_DIR})

set(MAIN_SRC src/rextr.cpp)

file(GLOB ENC_SRCS          "src/enc/*.cpp")
file(GLOB EXTR_SRCS         "src/extr/*.cpp")
file(GLOB REPACK_SRCS       "src/repack/*.cpp")
file(GLOB SPECIAL_SRCS      "src/special/*.cpp")
file(GLOB STRUCTURE_SRCS    "src/structure/*.cpp")
file(GLOB UTILS_SRCS        "src/utils/*.cpp")

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
    src/enc
    src/extr
    src/repack
    src/speical
    src/utils
    src
)

target_link_libraries(
    rextr 
PRIVATE
    ${OPENSSL_LIBRARIES}
)