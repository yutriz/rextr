#ifndef REXTR_EXTR_SCENE_HXX
#define REXTR_EXTR_SCENE_HXX

#include "src/extr/Block.hxx"

struct Scene {
    std::string m_md5; /* file associated */
    
    using TextBlockList = std::list<BasicBlock>;
    size_t m_num_blocks; /* nums of blocks */
    std::unique_ptr<TextBlockList> m_textblocks;
    
    explicit Scene(std::string md5, size_t num_blocks, 
                   std::unique_ptr<TextBlockList> &textblocks) :
        m_md5(md5), m_num_blocks(num_blocks),
        m_textblocks(std::move(textblocks)) {} 
};

#endif