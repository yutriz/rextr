#ifndef REXTR_UTILS_STRING_HPP
#define REXTR_UTILS_STRING_HPP

#include <string>

std::wstring stringToWstring(const std::string &str);
std::string wstringToString(const std::wstring &wstr);

size_t countBytes(const std::string &str);

#endif