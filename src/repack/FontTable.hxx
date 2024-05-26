#ifndef REXTR_REPACK_FONTTABLE_HXX
#define REXTR_REPACK_FONTTABLE_HXX

#include "src/enc/CodePoint.hxx"
#include "src/utils/Json.hxx"

#include <unordered_map>
#include <fstream>

using CharMap = std::unordered_map<cp_basic, bool>;

int renewMap(CharMap &cm, const Json &jscn,  std::string jkey);
int renewMap(CharMap &cm, const char *jfscn, std::string jkey);

int dumpMap(const CharMap &cm, std::ostream &os,  int cpl=8);
int dumpMap(const CharMap &cm, const char *ofile, int cpl=8);

#endif
