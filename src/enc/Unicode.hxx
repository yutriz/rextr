#ifndef REXTR_ENC_UNICODE_HXX
#define REXTR_ENC_UNICODE_HXX

#include "enc/CodePoint.hxx"

#include <string>

/* convert Code Point to Character */
std::string utf8Character(const CodePoint &cp);

/* Character to Code Point */
CodePoint utf8CodePoint(const std::string &u);

#endif