#ifndef REXTR_UTILS_HEX_HPP
#define REXTR_UTILS_HEX_HPP

#include <string>
#include <cstdint>

/**
 * 0x123abc to str"123abc" 
 * len: exactly length of string
 *      e.g. 0x1    len=2 -> "01"
 *           0x1234 len=4 -> "1234"
 */
std::string hex2Str(uint_least32_t hex, int len=2);

/**
 * hex2String for unsigned char*  
 */
std::string hexUchars2Str(const unsigned char* c, int n=1);

/**
 * hex2Str but longer. dont care length of string
 */
std::string hexLong2Str(uint64_t hex);

/**
 * "0123" to 0x123
 */
uint_least32_t strUintLeast32ToHex(const char* str);

size_t str2HexSizeT(const char* str);

#endif



