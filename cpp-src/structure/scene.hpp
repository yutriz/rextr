#ifndef REXTR_STRUCTURE_SCENE_HPP
#define REXTR_STRUCTURE_SCENE_HPP

#include "structure/block.hpp"

// typically a file with .scn suffix
struct Scene {
    std::string m_md5; /* file associated */
    
    using TextBlockList = std::list<Block>;
    size_t m_num_blocks; /* nums of blocks */
    std::unique_ptr<TextBlockList> m_textblocks;
    
    explicit Scene(
        std::string md5, 
        size_t num_blocks, 
        std::unique_ptr<TextBlockList> textblocks
    ) 
        : m_md5(md5)
        , m_num_blocks(num_blocks)
        , m_textblocks(std::move(textblocks))
    { } 
};

struct RepackScene {
    std::string m_md5; /* file associated */
    
    using TextRepackBlockList = std::list<RepackBlock>;
    size_t m_num_blocks; /* nums of blocks */
    std::unique_ptr<TextRepackBlockList> m_textblocks;
    
    explicit RepackScene (
        std::string md5, 
        size_t num_blocks, 
        std::unique_ptr<TextRepackBlockList> textblocks
    ) 
        : m_md5(md5)
        , m_num_blocks(num_blocks)
        , m_textblocks(std::move(textblocks))
    { } 
};

const std::string SPEC_KEYNAME_MD5SUM = "md5";
const std::string SPEC_KEYNAME_BLOCKS = "blocks";

#endif