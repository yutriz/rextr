#ifndef REXT_REPACK_PACKING_HXX
#define REXT_REPACK_PACKING_HXX

#include "repack/SceneR.hxx"
#include "enc/Encoding.hxx"

#include <fstream>

size_t repack_offset(SceneR_offset &scnro, const char *rawfile, std::ostream &os, 
                     int (*checkFunc)(SceneR_offset&, const char *));

size_t repack_offset_enc(SceneR_offset &scnro, const char *rawfile, 
                        Encoding &renc, std::ostream &os, 
                        int (*checkFunc)(SceneR_offset&, const char *));


#endif
