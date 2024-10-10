#ifndef REXT_EXTR_QUICKEXTR_HXX
#define REXT_EXTR_QUICKEXTR_HXX

#include "enc/Encoding.hxx"

void quickExtrJson(const char *fn, std::ostream &os, const Encoding &enc);
void quickExtrJson_SN1ps1(const char *fn, std::ostream &os, const Encoding &enc);

#endif