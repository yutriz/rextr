#ifndef REXT_EXTR_EXTRACT_HXX
#define REXT_EXTR_EXTRACT_HXX

/* test */
#include "src/extr/Block.hxx"
#include "src/extr/Scene.hxx"
#include "src/utils/Json.hxx"

#include <fstream>

Json Block2Json_full(const BasicBlock &blk);
Json Block2Json_simple(const BasicBlock &blk);
Json Block2Json_offset(const BasicBlock &blk);

Json Scene2Json_full(const Scene &scn);
Json Scene2Json_simple(const Scene &scn); 
Json Scene2Json_offset(const Scene &scn); 

size_t writeJson(const Json &j, std::ostream &os);
size_t writeJson(const Json &j, const char *f);

#endif