#include "utils/hex_utils.hpp"

#include <cstring>

/**
 * 0x123abc to str"123abc" 
 * len: exactly length of string
 *      e.g. 0x1    len=2 -> "01"
 *           0x1234 len=4 -> "1234"
 */
std::string hex2Str(uint_least32_t hex, int len) {
    char hexString[2*sizeof(uint_least32_t)+1];
    char print_format[10];
    sprintf(print_format, "%%0%ix", len);
    sprintf(hexString, print_format, hex);
    return std::string(hexString);
}

/**
 * hex2String for unsigned char*  
 */
std::string hexUchars2Str(const unsigned char* c, int n) {
    char hexString[2*n+1];
    for(int i=0; i<n; i++) {
        sprintf(hexString+2*i, "%02x", *c++);
    }
    return std::string(hexString);
}

/**
 * hex2Str but longer. dont care length of string
 */
std::string hexLong2Str(uint64_t hex) {
    char hexString[2*sizeof(uint64_t)+1];
    const char *print_format = "%x";
    sprintf(hexString, print_format, hex);
    return std::string(hexString);
}

/**
 * "0123" to 0x123
 */
uint_least32_t strUintLeast32ToHex(const char* str) {
    uint_least32_t ret;
    sscanf(str, "%x", &ret);
    return ret;
}

size_t str2HexSizeT(const char* str) {
    size_t ret;
    sscanf(str, "%lx", &ret);
    return ret;
}




