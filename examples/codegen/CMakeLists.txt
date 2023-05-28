#
# codegen



set(CODEGEN_TARGET codegen)
add_executable(${CODEGEN_TARGET} main.cpp codegen.cpp)

target_link_libraries(${CODEGEN_TARGET} PRIVATE ggml common common-ggml)

#
# codegen-quantize

set(CODEGEN_QT_TARGET codegen-quantize)
add_executable(${CODEGEN_QT_TARGET} quantize.cpp)

target_link_libraries(${CODEGEN_QT_TARGET} PRIVATE ggml common common-ggml)

# 
# codegen-serve

set(CODEGEN_SERVE_TARGET codegen-serve)
add_executable(${CODEGEN_SERVE_TARGET} serve.cpp codegen.cpp)
target_link_libraries(${CODEGEN_SERVE_TARGET} PRIVATE ggml common common-ggml)
find_package(Boost REQUIRED)
include_directories(${Boost_INCLUDE_DIRS})

if (GGML_STATIC)
    #add_link_options(-static-libgcc -static-libstdc++)
    SET(CMAKE_EXE_LINKER_FLAGS "-static -static-libgcc -static-libstdc++")
    SET_TARGET_PROPERTIES(${CODEGEN_TARGET} PROPERTIES 
LINK_SEARCH_END_STATIC 1)
    SET_TARGET_PROPERTIES(${CODEGEN_QT_TARGET} PROPERTIES 
LINK_SEARCH_END_STATIC 1)
SET_TARGET_PROPERTIES(${CODEGEN_SERVE_TARGET} PROPERTIES 
LINK_SEARCH_END_STATIC 1)
endif()