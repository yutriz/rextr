#ifndef REXT_UTILS_UNICODE_HPP
#define REXT_UTILS_UNICODE_HPP
// ref: http://www.zedwood.com/article/cpp-utf8-char-to-codepoint

#include <cstdint>
#include <string>

std::string intToUTF8Character(int cp);
int UTF8CodePointToInt(const std::string &u);

#endif