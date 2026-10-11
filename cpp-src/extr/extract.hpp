#ifndef REXTR_EXTR_EXTRACT_HPP
#define REXTR_EXTR_EXTRACT_HPP

#include "enc/encoding.hpp"
#include "structure/block.hpp"
#include "structure/scene.hpp"

#include <fstream>
#include <string>
#include <vector>

Block newBlock(
    std::vector<char> &chunk, 
    size_t &current_pos,
    size_t end_pos,
    const Encoding &enc,
    bool cjk_only, 
    int minimum_len=2 // minimum block text length
);

Scene newSceneFromFile(
    const std::string &filename, 
    const Encoding &enc, 
    bool cjk_only=0, 
    int minimum_len=2 // minimum block text length
);

#endif