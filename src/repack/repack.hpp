#ifndef REXT_REPACK_REPACK_HPP
#define REXT_REPACK_REPACK_HPP

#include "enc/encoding.hpp"
#include "structure/scene.hpp"

#include <fstream>
#include <string>

size_t repack(
    RepackScene &rscn, 
    Encoding &enc, 
    const std::string &origin_filepath,
    std::ostream &os, 
    bool is_little_endian = true, 
    bool do_validation = true
);

#endif
