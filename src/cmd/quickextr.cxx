#include "src/extr/QuickExtr.hxx"
#include "src/enc/Shiftjis.hxx"
#include "src/cmd/Option.hxx"

#include <fstream>

static constexpr option long_opts[] = {
    {"input",       1, NULL, 'i'},
    {"help",        0, NULL, 'h'},
    {"output",      1, NULL, 'o'},
    {"print",       0, NULL, 'p'},
    { NULL,         0, NULL,  0 }
};

static constexpr OptionDef opt_defs[] = {
  	{"input",   'i', 1, "file",  "raw data"},
    {"help",    'h', 0, "",      "print help options"},
    {"output",  'o', 1, "file",  "default: input_file.qd.json(will overwrite)"},
    {"print",   'p', 0, "",      "print to stdout"},
};

static void printHelp() {
    printf("\n");
    printf("Extract recognized texts in Shift-JIS from file\n");
    printf("Usage: quickdump -i filename (-o filename)\n");
    for(const auto &i : opt_defs)
        PrintOpts(i);
    exit(0);
}

const char *short_opts = "hi:o::p";
bool f_ifile = 0;   char *ifile;
bool f_ofile = 0;   char *ofile;
bool f_print = 0;

int getOptions(int argc, char **argv) {
    int c;
    while ((c = getopt_long(argc, argv, short_opts, long_opts, NULL)) != -1) {
        switch (c)
        {
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
        case 'p':
            f_print = 1;
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

    if (!f_ifile) {
        fprintf(stderr, "no input file.\n");
        printHelp();
    }

    auto sjis_copy = Enc_sjis;
    // add conversion you found
    // make it a para?
    sjis_copy.add({CodePoint_t::B8, 0x0a}, {CodePoint_t::B8, 0x0a}); //SN1 2
    //sjis_copy.add({CodePoint_t::CJK, 0x0000}, {CodePoint_t::B8, 0x0a}); 

    std::string output;
    if (f_ofile)
        output = std::string(ofile);
    if (!f_ofile)
        output = addSuffix(std::string(ifile), ".qe.json");

    std::ofstream os(output);
    quickExtrJson(ifile, os, sjis_copy);
    os.close();
    
    if (f_print == 1) 
        quickExtrJson(ifile, std::cout, sjis_copy);

    fprintf(stdout, "Done!\n");

    return 0;
}



