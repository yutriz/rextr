CXX = g++
BUILDDIR = build
OBJDIR = $(BUILDDIR)/obj
PROJECTDIR = ..
CXXFLAGS = -I$(PROJECTDIR) 
CXXFLAGS_SSL = -lcrypto -lssl -Wno-deprecated-declarations
CMDS = quickextr extr quickrepack nodupl

all: mkdir_obj $(CMDS) 

mkdir_obj:
	if [ ! -d $(BUILDDIR)/obj ]; then mkdir -p $(BUILDDIR)/obj; fi

# utils 
_UTILS = utils_hash.o
UTILS = $(patsubst %, $(OBJDIR)/%, $(_UTILS))

$(OBJDIR)/utils_hash.o: $(PROJECTDIR)/src/utils/Hash.cxx
	$(CXX) -c $< $(CXXFLAGS) $(CXXFLAGS_SSL) -o $@ 

# enc
_ENC = enc_encoding.o enc_unicode.o
ENC = $(patsubst %, $(OBJDIR)/%, $(_ENC))

$(OBJDIR)/enc_encoding.o: $(PROJECTDIR)/src/enc/Encoding.cxx 
	$(CXX) -c $< $(CXXFLAGS) -o $@ 
$(OBJDIR)/enc_unicode.o: $(PROJECTDIR)/src/enc/Unicode.cxx 
	$(CXX) -c $< $(CXXFLAGS) -o $@ 

# extr
_EXTR = extr_read.o extr_extract.o extr_quickextr.o
EXTR = $(patsubst %, $(OBJDIR)/%, $(_EXTR))

$(OBJDIR)/extr_read.o: $(PROJECTDIR)/src/extr/Read.cxx 
	$(CXX) -c $< $(CXXFLAGS) $(CXXFLAGS_SSL) -o $@ 
$(OBJDIR)/extr_extract.o: $(PROJECTDIR)/src/extr/Extract.cxx
	$(CXX) -c $< $(CXXFLAGS) -o $@ 
$(OBJDIR)/extr_quickextr.o: $(PROJECTDIR)/src/extr/QuickExtr.cxx
	$(CXX) -c $< $(CXXFLAGS) $(CXXFLAGS_SSL) -o $@ 

# repack
_REPACK = repack_check.o repack_readr.o repack_packing.o repack_fontt.o
REPACK = $(patsubst %, $(OBJDIR)/%, $(_REPACK))

$(OBJDIR)/repack_check.o: $(PROJECTDIR)/src/repack/Check.cxx
	$(CXX) -c $< $(CXXFLAGS) $(CXXFLAGS_SSL) -o $@ 
$(OBJDIR)/repack_readr.o: $(PROJECTDIR)/src/repack/ReadR.cxx
	$(CXX) -c $< $(CXXFLAGS) -o $@
$(OBJDIR)/repack_packing.o: $(PROJECTDIR)/src/repack/Packing.cxx
	$(CXX) -c $< $(CXXFLAGS) -o $@ 
$(OBJDIR)/repack_fontt.o: $(PROJECTDIR)/src/repack/FontTable.cxx
	$(CXX) -c $< $(CXXFLAGS) -o $@ 

# cmds
quickextr: $(PROJECTDIR)/src/cmd/quickextr.cxx $(UTILS) $(ENC) $(EXTR)
	$(CXX) $^ $(CXXFLAGS) $(CXXFLAGS_SSL) -o $(BUILDDIR)/quickextr

extr: $(PROJECTDIR)/src/cmd/extr.cxx $(UTILS) $(ENC) $(EXTR)
	$(CXX) $^ $(CXXFLAGS) $(CXXFLAGS_SSL) -o $(BUILDDIR)/extr

quickrepack: $(PROJECTDIR)/src/cmd/quickrepack.cxx $(UTILS) $(ENC) $(REPACK)
	$(CXX) $^ $(CXXFLAGS) $(CXXFLAGS_SSL) -o $(BUILDDIR)/quickrepack

nodupl: $(PROJECTDIR)/src/cmd/nodupl.cxx $(UTILS) $(REPACK)
	$(CXX) $^ $(CXXFLAGS) $(CXXFLAGS_SSL) -o $(BUILDDIR)/nodupl

clean: 
	rm $(BUILDDIR)/* -rf 
