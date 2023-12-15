

set(HIGHS_DIR "")

if (FAST_BUILD)
  if(NOT TARGET highs)
    include("${CMAKE_CURRENT_LIST_DIR}/highs-targets.cmake")
  endif()

  set(HIGHS_LIBRARIES highs)
else()
  if(NOT TARGET libhighs)
    include("${CMAKE_CURRENT_LIST_DIR}/highs-targets.cmake")
  endif()

  set(HIGHS_LIBRARIES libhighs)
endif() 

set(HIGHS_INCLUDE_DIRS "/Users/ssmehta/.cargo/registry/src/index.crates.io-6f17d22bba15001f/highs-sys-1.6.0/HiGHS/src;/Users/ssmehta/Documents/Forecasting/RustAttempt/portfolio_optimization/target/debug/build/highs-sys-8c46162957c444af/out/build")

set(HIGHS_FOUND TRUE)

include(CMakeFindDependencyMacro)
find_dependency(ZLIB)
