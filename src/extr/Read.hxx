#ifndef REXTR_EXTR_READ_HXX
#define REXTR_EXTR_READ_HXX

#include "enc/Encoding.hxx"
#include "extr/Block.hxx"
#include "extr/Scene.hxx"

#include <fstream>

BasicBlock
newBlock(std::istream &is, const Encoding &enc, bool cjk_only=0, int minimum_len=2);

Scene
newScene(const char *filename, const Encoding &enc, bool cjk_only=0, int minimum_len=2);

#endif