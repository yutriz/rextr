#ifndef REXTR_UTILS_HEX_HXX
#define REXTR_UTILS_HEX_HXX

#include <cstring>
#include <string>
#include <cstdint>

/**
 * 0x123abc to str"123abc" 
 * len: exactly length of string
 *      e.g. 0x1    len=2 -> "01"
 *           0x1234 len=4 -> "1234"
 */
inline std::string 
hex2str(uint_least32_t hex, int len=2) {
    char hexString[2*sizeof(uint_least32_t)+1];
    char print_format[10];
    sprintf(print_format, "%%0%ix", len);
    sprintf(hexString, print_format, hex);
    return std::string(hexString);
}

/**
 * hex2String for unsigned char*  
 */
inline std::string
hex2str_uchars(const unsigned char* c, int n=1) {
    char hexString[2*n+1];
    for(int i=0; i<n; i++) {
        sprintf(hexString+2*i, "%02x", *c++);
    }
    return std::string(hexString);
}

/**
 * hex2str but longer. dont care length of string
 */
inline std::string 
hex2String_long(uint64_t hex) {
    char hexString[2*sizeof(uint64_t)+1];
    const char *print_format = "%x";
    sprintf(hexString, print_format, hex);
    return std::string(hexString);
}

/**
 * "0123" to 0x123
 */
inline uint_least32_t 
str2hex_uint_least32(const char* str) {
    uint_least32_t ret;
    sscanf(str, "%x", &ret);
    return ret;
}

inline size_t
str2hex_size_t(const char* str) {
    size_t ret;
    sscanf(str, "%lx", &ret);
    return ret;
}

#endif



