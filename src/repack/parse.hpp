#ifndef REXTR_REPACK_PARSE_HPP
#define REXTR_REPACK_PARSE_HPP

#include "structure/block.hpp"
#include "structure/scene.hpp"
#include "utils/json_utils.hpp"

RepackBlock parseRepackBlock(const Json &j); 

RepackScene parseRepackScene(const Json &j);

#endif