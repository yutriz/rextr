#ifndef REXT_EXTR_DUMP_HPP
#define REXT_EXTR_DUMP_HPP

#include "structure/block.hpp"
#include "structure/scene.hpp"
#include "utils/json_utils.hpp"

Json dumpBlock(const Block &blk);

Json dumpScene(const Scene &scn);

#endif