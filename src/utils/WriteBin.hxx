#ifndef REXT_UTILS_WB_HXX
#define REXT_UTILS_WB_HXX

#include "enc/Encoding.hxx"

#include <cstdint>
#include <cstring>
#include <fstream>

/**
 * oops the endian! 
 * n = char numbers 
 *    0x11    char 1
 *    0x1234  char 2
 */
void writeBin_val(std::ostream &os, uint_least32_t val, const short n);

/**
 * hex string like "0123456789abcdef"
 */
size_t writeBin_hexStr(std::ostream &os, std::string &str);

/**
 * consist of only wide char 
 */
size_t writeBin_wideOnly(std::ostream &os, std::string &str);

size_t writeBin_mixed(std::ostream &os, std::string &str);

size_t writeBin_mixed_enc(std::ostream &os, std::string &str, Encoding &enc);

#endif