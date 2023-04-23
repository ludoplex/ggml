#
# codegen

set(TEST_TARGET codegen)
add_executable(${TEST_TARGET} main.cpp codegen.cpp)
target_link_libraries(${TEST_TARGET} PRIVATE ggml common common-ggml)

#
# codegen-quantize

set(TEST_TARGET codegen-quantize)
add_executable(${TEST_TARGET} quantize.cpp)
target_link_libraries(${TEST_TARGET} PRIVATE ggml common common-ggml)

# 
# codegen-serve

set(TEST_TARGET codegen-serve)
add_executable(${TEST_TARGET} serve.cpp codegen.cpp)
target_link_libraries(${TEST_TARGET} PRIVATE ggml common common-ggml)
find_package(Boost REQUIRED)
include_directories(${Boost_INCLUDE_DIRS})
