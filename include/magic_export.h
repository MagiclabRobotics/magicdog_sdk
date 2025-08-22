#pragma once
// 1
#ifdef __cplusplus
extern "C" {
#endif

#if defined _WIN32 || defined __CYGWIN__
  #ifdef __GNUC__
    #define MAGIC_EXPORT_API __attribute__((dllexport))
  #else
    #define MAGIC_EXPORT_API __declspec(dllexport)
  #endif
#else
  #define MAGIC_EXPORT_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
}
#endif