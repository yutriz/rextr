#include "src/repack/Packing.hxx"
#include "src/repack/ReadR.hxx"
#include "src/repack/Check.hxx"
#include "src/cmd/Option.hxx"

const char *short_opts = "c:hi:o::r:";
bool f_ifile = 0;   char *ifile;
bool f_ofile = 0;   char *ofile;
bool f_rfile = 0;   char *rfile;
bool f_cjk   = 0;   char *cjk;

static constexpr option long_opts[] = {
    {"cjk",         1, NULL, 'c'},
    {"input",       1, NULL, 'i'},
    {"help",        0, NULL, 'h'},
    {"output",      1, NULL, 'o'},
    {"raw",         1, NULL, 'r'},
    { NULL,         0, NULL,  0 }
};

static constexpr OptionDef opt_defs[] = {
    {"cjk",     'c', 0, "",      "cjk table"},
  	{"input",   'i', 1, "file",  "raw data"},
    {"help",    'h', 0, "",      "print help options"},
    {"output",  'o', 1, "file",  "default: raw_file.repack"},
    {"raw",     'r', 0, "",      "raw file, hash checked"},
};

static void printHelp() {
    printf("\n");
    printf("Repack from json file and original raw file(Custom encoding)\n");
    printf("Usage: quickrepack -r filename -i filename -c cjk_table(-b 8bit_tbale -o filename)\n");
    for(const auto &i : opt_defs)
        PrintOpts(i);
    exit(0);
}

int getOptions(int argc, char **argv) {
    int c;
    while ((c = getopt_long(argc, argv, short_opts, long_opts, NULL)) != -1) {
        switch (c)
        {
        case 'c':
            f_cjk = 1;
            cjk = optarg;
            break;
        case 'h':
            printHelp();
            break;
        case 'i':
            f_ifile = 1;
            ifile = optarg;
            break;
        case 'o':
            f_ofile = 1;
            ofile = optarg;
            break;
        case 'r':
            f_rfile = 1;
            rfile = optarg;
            break;
        case '?':
            fprintf(stderr, "%s: option `-%c' is invalid: ignored\n",
                    argv[0], optopt);
            break;
        }
    }
    return 0;
}

int main(int argc, char *argv[]) {
    getOptions(argc, argv);

    if (!f_ifile || !f_rfile) {
        fprintf(stderr, "no input json file and raw file.\n");
        printHelp();
    }

    std::string output;
    if (f_ofile)
        output = std::string(ofile);
    if (!f_ofile)
        output = addSuffix(std::string(rfile), ".repack");
    
    std::ofstream ofs(output, std::ios::binary);
    SceneR_offset scnro = readSceneR_offset(ifile);

    auto enc = newEncoding_cjk(cjk);
    enc->add(CodePoint{CodePoint_t::B8, 0x0a}, CodePoint{CodePoint_t::B8, 0x0a});

    repack_offset_enc(scnro, rfile, *enc, ofs, checkSceneR_offset);
    ofs.close();
}