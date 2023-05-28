cmake_minimum_required (VERSION 3.0)
project(ggml VERSION 0.1.0)

set(CMAKE_EXPORT_COMPILE_COMMANDS "on")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/lib")

if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
    set(GGML_STANDALONE ON)
    include(cmake/GitVars.cmake)
    include(cmake/BuildTypes.cmake)
else()
    set(GGML_STANDALONE OFF)
endif()


# options
option(GGML_STATIC                 "ggml: static link libraries"                          OFF)

option(GGML_ALL_WARNINGS            "ggml: enable all compiler warnings"                   ON)
option(GGML_ALL_WARNINGS_3RD_PARTY  "ggml: enable all compiler warnings in 3rd party libs" OFF)

option(GGML_SANITIZE_THREAD         "ggml: enable thread sanitizer"    OFF)
option(GGML_SANITIZE_ADDRESS        "ggml: enable address sanitizer"   OFF)
option(GGML_SANITIZE_UNDEFINED      "ggml: enable undefined sanitizer" OFF)

option(GGML_BUILD_TESTS             "ggml: build tests"    ${GGML_STANDALONE})
option(GGML_BUILD_EXAMPLES          "ggml: build examples" ${GGML_STANDALONE})

option(GGML_PERF                    "ggml: enable perf timings"          OFF)
option(GGML_NO_ACCELERATE           "ggml: disable Accelerate framework" OFF)
option(GGML_OPENBLAS                "ggml: use OpenBLAS"                 OFF)
option(GGML_CUBLAS                  "ggml: use cuBLAS"                   OFF)

# sanitizers

if (GGML_SANITIZE_THREAD)
    set(CMAKE_C_FLAGS   "${CMAKE_C_FLAGS}   -fsanitize=thread")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=thread")
endif()

if (GGML_SANITIZE_ADDRESS)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}     -fsanitize=address -fno-omit-frame-pointer")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=address -fno-omit-frame-pointer")
endif()

if (GGML_SANITIZE_UNDEFINED)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}     -fsanitize=undefined")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=undefined")
endif()


# instruction set specific
option(GGML_AVX                    "llama: enable AVX"                                     ON)
option(GGML_AVX2                   "llama: enable AVX2"                                    ON)
option(GGML_AVX512                 "llama: enable AVX512"                                  OFF)
option(GGML_FMA                    "llama: enable FMA"                                     ON)
# in MSVC F16C is implied with AVX2/AVX512
if (NOT MSVC)
    option(GGML_F16C               "llama: enable F16C"                                    ON)
endif()


if (${CMAKE_SYSTEM_PROCESSOR} MATCHES "arm" OR ${CMAKE_SYSTEM_PROCESSOR} MATCHES "aarch64")
    message(STATUS "ARM detected")
    if (MSVC)
        # TODO: arm msvc?
    else()
        if (${CMAKE_SYSTEM_PROCESSOR} MATCHES "aarch64")
            add_compile_options(-mcpu=native)
        endif()
        # TODO: armv6,7,8 version specific flags
    endif()
elseif (${CMAKE_SYSTEM_PROCESSOR} MATCHES "^(x86_64|i686|AMD64)$")
    message(STATUS "x86 detected")
    if (MSVC)
        if (GGML_AVX512)
            message(STATUS "using AVX512")
            add_compile_options(/arch:AVX512)
        elseif (GGML_AVX2)
            message(STATUS "using AVX2")
            add_compile_options(/arch:AVX2)
        elseif (GGML_AVX)
            message(STATUS "using AVX")
            add_compile_options(/arch:AVX)
        endif()
    else()
        if (GGML_F16C)
            message(STATUS "using F16c")
            add_compile_options(-mf16c)
        endif()
        if (GGML_FMA)
            message(STATUS "using FMA")
            add_compile_options(-mfma)
        endif()
        if (GGML_AVX)
            message(STATUS "using AVX")
            add_compile_options(-mavx)
        endif()
        if (GGML_AVX2)
            message(STATUS "using AVX2")
            add_compile_options(-mavx2)
        endif()
        if (GGML_AVX512)
            message(STATUS "using AVX512")
            add_compile_options(-mavx512f)
            # add_compile_options(-mavx512cd)
            # add_compile_options(-mavx512dq)
            # add_compile_options(-mavx512bw)
        endif()
    endif()
else()
    # TODO: support PowerPC
    message(STATUS "Unknown architecture")
endif()


option(GGML_OPENBLAS               "ggml: use OpenBLAS"                                   OFF)


#set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -ffast-math")
#set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -march=native")
#set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -mcpu=native")

# dependencies

set(CMAKE_C_STANDARD   11)
set(CMAKE_CXX_STANDARD 11)

find_package(Threads REQUIRED)

if (APPLE AND GGML_ACCELERATE)
    find_library(ACCELERATE_FRAMEWORK Accelerate)
    if (ACCELERATE_FRAMEWORK)
        message(STATUS "Accelerate framework found")

        add_compile_definitions(GGML_USE_ACCELERATE)
        set(GGML_EXTRA_LIBS ${GGML_EXTRA_LIBS} ${ACCELERATE_FRAMEWORK})
    else()
        message(WARNING "Accelerate framework not found")
    endif()
endif()
if (GGML_OPENBLAS)
    if (GGML_STATIC)
        set(BLA_STATIC ON)
    endif()

    set(BLA_VENDOR OpenBLAS)
    find_package(BLAS)
    if (BLAS_FOUND)
        message(STATUS "OpenBLAS found")

        add_compile_definitions(GGML_USE_OPENBLAS)
        #add_link_options(${BLAS_LIBRARIES})
        add_compile_options(${BLAS_LINKER_FLAGS})
        set(GGML_EXTRA_LIBS ${GGML_EXTRA_LIBS} ${BLAS_LIBRARIES})

        # find header file
        set(OPENBLAS_INCLUDE_SEARCH_PATHS
            /usr/include
            /usr/include/openblas
            /usr/include/openblas-base
            /usr/local/include
            /usr/local/include/openblas
            /usr/local/include/openblas-base
            /opt/OpenBLAS/include
            $ENV{OpenBLAS_HOME}
            $ENV{OpenBLAS_HOME}/include
            )

        include_directories(${BLAS_INCLUDE_DIRS})

        find_path(OPENBLAS_INC NAMES cblas.h PATHS ${OPENBLAS_INCLUDE_SEARCH_PATHS})
        add_compile_options(-I${OPENBLAS_INC})
    else()
        message(WARNING "OpenBLAS not found")
    endif()
endif()

if (NOT MSVC)
    if (GGML_STATIC)
        add_link_options(-static)
        if (MINGW OR GGML_CUBLAS)
            add_link_options(-static-libgcc -static-libstdc++)
        endif()
    endif()
    if (GGML_GPROF)
        add_compile_options(-pg)
    endif()
    if (GGML_NATIVE)
        add_compile_options(-march=native)
    endif()
endif()

# main

if (NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
    set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "RelWithDebInfo")
endif ()

add_subdirectory(src)

if (GGML_BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif ()

if (GGML_BUILD_EXAMPLES)
    add_subdirectory(examples)
endif ()
