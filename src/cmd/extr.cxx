#include "enc/Encoding.hxx"
#include "extr/Read.hxx"
#include "extr/Extract.hxx"
#include "utils/Hex.hxx"
#include "cmd/Option.hxx"

static const char *short_opts = "a:b:c:hi:o:s";

bool f_b8t    = false;  char *b8t;
bool f_cjkt   = false;  char *cjkt;
bool f_ifile  = false;  char *ifile;
bool f_ofile  = false;  char *ofile;
bool f_simple = false;

static constexpr option long_opts[] = {
    {"add",       1, NULL, 'a'}, // unimplemented
    {"b8",        1, NULL, 'b'},
    {"cjk",       1, NULL, 'c'},
    {"help",      0, NULL, 'h'},
    {"input",     1, NULL, 'i'},
    {"output",    1, NULL, 'o'},
    {"simple",    0, NULL, 's'},
    { NULL, 0, NULL, 0 }
};

static constexpr OptionDef opt_defs[] = {
    {"add extras",  'a', 1, "cp pair",  ""},
  	{"8bit_table",  'b', 1, "file",     ""},
    {"cjk_table",   'c', 1, "file",     ""},
    {"help",        'h', 0, "",         "print help options"},
    {"input file",  'i', 1, "file",     ""},
    {"output file", 'o', 1, "file",     ""},
    {"simple mode", 's', 0, "",         ""}
};

static void PrintHelp() {
    printf("Extract recognized text in given encoding from file");
    printf("Usage:\n");
    printf("  fullextr -b b8_table -c cjk_table -i filename (-o filename)\n");
    for(const auto &i : opt_defs)
        PrintOpts(i);
    exit(0);
}

int GetOptions(int argc, char **argv) {
    int c;
    while ((c = getopt_long(argc, argv, short_opts, long_opts, NULL)) != -1) {
        switch (c)
        {
        //case 'a':
        // not implemented
        case 'b':
            f_b8t = 1;
            b8t = optarg;
            break;
        case 'c':
            f_cjkt = 1;
            cjkt = optarg;
            break;
        case 'h':
            PrintHelp();
            break;
        case 'i':
            f_ifile = 1;
            ifile = optarg;
            break;
        case 'o':
            f_ofile = 1;
            ofile = optarg;
            break;
        case 's':
            f_simple = 1;
            break;
        case '?':
            fprintf(stderr, "%s: option `-%c' is invalid: ignored\n",
                argv[0], optopt);
            break;
        }
    }
    return 0;
}

int main(int argc, char **argv) {
    GetOptions(argc, argv);
    if(!ifile || !b8t || !cjkt) {
        fprintf(stdout, "need b8+cjk table and input file\n");
        exit(0);
    }

    Encoding* enc = newEncoding(b8t, cjkt);

    // add extras
    // enc->add({B8,0x0a},{B8,0x0a}); 

    Scene scn = newScene(ifile, *enc, 1);
    fprintf(stdout, "scn read! generating json\n");
    Json j;

    std::string output;
    if (f_ofile)
        output = std::string(ofile);
    if (!f_ofile)
        output = addSuffix(std::string(ifile), ".json");
    if(f_simple)
        output = addSuffix(std::string(ifile), ".simple.json");

    if(f_simple)
        j = Scene2Json_simple(scn);
    else 
        j = Scene2Json_full(scn);
  
    writeJson(j, output.c_str());
}
