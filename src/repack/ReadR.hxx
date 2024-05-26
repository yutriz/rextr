#ifndef REXTR_REPACK_READR_HXX
#define REXTR_REPACK_READR_HXX

#include "src/repack/SceneR.hxx"
#include "src/utils/Json.hxx"

BlockR_full Json2BlockR_full(const Json &j);
SceneR_full Json2SceneR_full(const Json &j);
SceneR_full readSceneR_full(const char *jf);

BlockR_offset Json2BlockR_offset(const Json &j);
SceneR_offset Json2SceneR_offset(const Json &j);
SceneR_offset readSceneR_offset(const char *jf);

#endif