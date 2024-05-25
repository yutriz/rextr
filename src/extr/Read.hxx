#ifndef REXTR_EXTR_READ_HXX
#define REXTR_EXTR_READ_HXX

#include "src/enc/Encoding.hxx"
#include "src/extr/Block.hxx"
#include "src/extr/Scene.hxx"

#include <fstream>

BasicBlock
newBlock(std::istream &is, const Encoding &enc, bool cjk_only=0, int minimum_len=2);

Scene
newScene(const char *filename, const Encoding &enc, bool cjk_only=0, int minimum_len=2);

#endif