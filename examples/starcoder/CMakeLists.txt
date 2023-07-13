#
# starcoder

set(TEST_TARGET starcoder)
add_executable(${TEST_TARGET} main.cpp)
target_link_libraries(${TEST_TARGET} PRIVATE ggml common common-ggml)

#
# starcoder-quantize

set(TEST_TARGET starcoder-quantize)
add_executable(${TEST_TARGET} quantize.cpp)
target_link_libraries(${TEST_TARGET} PRIVATE ggml common common-ggml)


set(TEST_TARGET starcoder-serve)
add_executable(${TEST_TARGET} serve.cpp main.cpp)
target_link_libraries(${TEST_TARGET} PRIVATE ggml common common-ggml)
find_package(Boost REQUIRED)
include_directories(${Boost_INCLUDE_DIRS})