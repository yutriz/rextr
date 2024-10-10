cmake_minimum_required(VERSION 3.9.1)
project(rextr)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "-Wno-deprecated-declarations")

include_directories(src)

find_package(OpenSSL REQUIRED)
include_directories(${OPENSSL_INCLUDE_DIR})

make_directory(./cmds)
aux_source_directory(src/enc ENC)
aux_source_directory(src/extr EXTR)
aux_source_directory(src/repack REPACK)
aux_source_directory(src/utils UTILS)


add_executable(
    quickextr
    src/cmd/quickextr.cxx
    ${ENC}
    ${EXTR}
    ${UTILS}
)
target_link_libraries(
    quickextr
PRIVATE
    ${OPENSSL_LIBRARIES}
)

# add_executable(
#     quickextr_ps1
#     src/cmd/quickextr_ps1.cxx
#     ${ENC}
#     ${EXTR}
#     ${UTILS}
# )
# target_link_libraries(
#     quickextr_ps1
# PRIVATE
#     ${OPENSSL_LIBRARIES}
# )


add_executable(
    extr
    src/cmd/extr.cxx
    ${ENC}
    ${EXTR}
    ${UTILS}
)
target_link_libraries(
    extr 
PRIVATE
    ${OPENSSL_LIBRARIES}
)

add_executable(
    quickrepack 
    src/cmd/quickrepack.cxx
    ${ENC}
    ${REPACK}
    ${UTILS}
)
target_link_libraries(
    quickrepack 
PRIVATE
    ${OPENSSL_LIBRARIES}
)

add_executable(
    quickrepack_enc
    src/cmd/quickrepack_enc.cxx
    ${ENC}
    ${REPACK}
    ${UTILS}
)
target_link_libraries(
    quickrepack_enc 
PRIVATE
    ${OPENSSL_LIBRARIES}
)


add_executable(
    nodupl
    src/cmd/nodupl.cxx
    ${ENC}
    ${REPACK}
    ${UTILS}
)
target_link_libraries(
    nodupl
PRIVATE
    ${OPENSSL_LIBRARIES}
)