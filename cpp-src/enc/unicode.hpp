#ifndef REXTR_ENC_UNICODE_HPP
#define REXTR_ENC_UNICODE_HPP

#include "enc/code_point.hpp"

#include <string>

/* convert Code Point to Character */
std::string UTF8Character(const CodePoint &cp);

/* Character to Code Point */
CodePoint UTF8CodePoint(const std::string &u);

#endif