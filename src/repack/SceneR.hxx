#ifndef REXT_REPACK_SCENER_HXX
#define REXT_REPACK_SCENER_HXX

#include "repack/BlockR.hxx"

#include <memory>
#include <list>

struct SceneR_full { 
    std::string m_hash;

    using BlockRList = std::list<BlockR_full>;
    std::unique_ptr<BlockRList> m_blks;
    
    explicit 
    SceneR_full(std::string hash, std::unique_ptr<BlockRList> &blks):
        m_hash(hash), m_blks(std::move(blks)) {}
};

/**
 * Type 1: Standard 
 */


/**
 *  Type 2: offset 
 */
struct SceneR_offset {
    std::string m_hash;

    using BlockRList = std::list<BlockR_offset>;
    std::unique_ptr<BlockRList> m_blks;

    explicit 
    SceneR_offset(std::string hash, std::unique_ptr<BlockRList> &blks):
        m_hash(hash), m_blks(std::move(blks)) {}
};

/**
 *  Type 3: Relative
 */

#endif