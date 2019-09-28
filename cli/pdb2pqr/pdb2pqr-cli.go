package main

import (
	// "flag"

	"fmt"
	"io/ioutil"
	"os"
	"path"
	"strconv"

	flag "github.com/spf13/pflag"

	"../rest"
)

type commandLine struct {
	OptionsFlagSet *flag.FlagSet
	jobid          string

	// Input/Output names
	pdbFilename string
	pqrFilename string

	// System Options
	version bool
	help    bool

	// Mandatory flags - user chooses one
	forcefield     string
	userForcefield string
	keepClean      bool

	// Titration state calculation options
	phCalcMethod    string
	phValue         float64
	propkaReference string
	propkaVerbose   bool
	pdb2pkaOut      string
	pdb2pkaResume   bool
	pdie            float64
	sdie            float64
	pairene         float64

	// General options
	apbsInput     bool
	assignOnly    bool
	chain         bool
	dropWater     bool
	forcefieldOut string
	ligand        string
	neutralN      bool
	neutralC      bool
	nodeBump      bool
	noOpts        bool
	typemap       bool
	usernames     string
	verbose       bool
	whitespace    bool
	includeHeader bool

	// Extension options -- not included at the moment

	// Misc.
	flagMap map[string]interface{}
}

type form struct {
	DEBUMP        string  `json:"DEBUMP"`
	FF            string  `json:"FF"`
	FFOUT         string  `json:"FFOUT"`
	INPUT         string  `json:"INPUT"`
	LIGANDFILE    string  `json:"LIGANDFILE"`
	NAMESFILE     string  `json:"NAMESFILE"`
	OPT           string  `json:"OPT"`
	OPTIONS       string  `json:"OPTIONS"`
	PDBFILE       string  `json:"PDBFILE"`
	PDBID         string  `json:"PDBID"`
	PDBSOURCE     string  `json:"PDBSOURCE"`
	PH            float64 `json:"PH"`
	PKACALCMETHOD string  `json:"PKACALCMETHOD"`
	USERFFFILE    string  `json:"USERFFFILE"`
}

func (c *commandLine) Init() {
	// Mandatory flags - user chooses one
	flag.StringVar(&c.forcefield, "ff", "", "The forcefield to use - currently amber, charmm, parse, tyl06, peoepb and swanson are supported.")
	flag.StringVar(&c.userForcefield, "userff", "", "A user-created forcefield file. Requires --usernames and overrides --ff.")
	flag.BoolVar(&c.keepClean, "clean", false, "Do no optimization, atom addition, or parameter assignment, just return the original PDB file in aligned format. Overrides --ff and --userff options.")

	// Dependent flags - whether it's used depends on option chosen above

	/*** Optional flags ***/

	// Titration state calculation options
	flag.StringVar(&c.phCalcMethod, "ph-calc-method", "", "Method used to calculate ph values. If a pH calculation method is selected, pKa values will be calculated and titratable residues potentially modified after comparison with the pH value supplied by --with_ph for each titratable residue")
	flag.Float64Var(&c.phValue, "with-ph", 7, "Method used to calculate ph values. If a pH calculation method is selected, pKa values will be calculated and titratable residues potentially modified after comparison with the pH value supplied by --with_ph for each titratable residue")
	flag.StringVar(&c.jobid, "id", rest.GetNewID(), "Specify custom job identifier for execution. Defaults to randomly generated ID.")

	// PROPKA
	flag.StringVar(&c.propkaReference, "propka-reference", "", "Setting which reference to use for stability calculations. See PROPKA 3.0 documentation.")
	flag.BoolVar(&c.propkaVerbose, "propka-verbose", false, "Print extra proPKA information to stdout. WARNING: This produces an incredible amount of output.")

	// PDB2PKA
	pdb2pkaOutDefault := "pdb2pka_output"
	pdieDefault := 8
	sdieDefault := 80
	var paireneDefault float64
	paireneDefault = 1.0
	// paireneDefault := 1.0
	flag.StringVar(&c.pdb2pkaOut, "pdb2pka-out", pdb2pkaOutDefault, "Output directory for PDB2PKA results. Defaults to "+pdb2pkaOutDefault)
	flag.BoolVar(&c.pdb2pkaResume, "pdb2pka-resume", false, "Resume run from state saved in output directory.")
	flag.Float64Var(&c.pdie, "pdie", float64(pdieDefault), "Protein dielectric constant. Defaults to "+strconv.Itoa(pdieDefault))
	flag.Float64Var(&c.sdie, "sdie", float64(sdieDefault), "Solvent dielectric constant. Defaults to "+strconv.Itoa(sdieDefault))
	flag.Float64Var(&c.pairene, "pairene", paireneDefault, "Cutoff energy in kT for calculating non charged-charged interaction energies. Default: "+strconv.FormatFloat(paireneDefault, 'g', 23, 64))

	// General options
	// GeneralFlags := flag.NewFlagSet("General Options", flag.ExitOnError)
	flag.BoolVar(&c.apbsInput, "apbs-input", false, "Create a template APBS input file based on the generated PQR file. Also create a Python pickle for using these parameters in other programs.")
	flag.BoolVar(&c.assignOnly, "assign-only", false, "Only assign charges and radii - do not add atoms, debump, or optimize.")
	flag.BoolVar(&c.chain, "chain", false, "Keep the PDB chain ID in the output PQR file.")
	flag.BoolVar(&c.dropWater, "drop-water", false, "Drop waters before processing protein. Currently recognized and deleted are the following water types: HOH, WAT")
	flag.StringVar(&c.forcefieldOut, "ffout", "", "Instead of using the standard canonical naming scheme for residue and atom names, use the names from the given forcefield. Currently amber, charmm, parse, tyl06, peoepb and swanson are supported.")
	flag.StringVar(&c.ligand, "ligand", "", "Calculate the parameters for the ligand in mol2 format at the given path. PDB2PKA must be compiled.")
	flag.BoolVar(&c.neutralN, "neutraln", false, "Make the N-terminus of this protein neutral (default charge state is determined by pH and pKa). Requires PARSE force field.")
	flag.BoolVar(&c.neutralC, "neutralc", false, "Make the C-terminus of this protein neutral (default is charged). Requires PARSE force field.")
	flag.BoolVar(&c.nodeBump, "nodebump", true, "Do not perform the debumping operation to remove steric clashes. See debumping for more information.")
	flag.BoolVar(&c.noOpts, "noopts", true, "Do not perform hydrogen bond optimization. See hbondopt for more information.")
	flag.BoolVar(&c.typemap, "typemap", false, "Create a map of atom types in the molecule.")
	flag.StringVar(&c.usernames, "usernames", "", "The user created names file to use. Required if using --userff.")
	flag.BoolVarP(&c.verbose, "verbose", "v", false, "Print additional information to stdout.")
	flag.BoolVar(&c.whitespace, "whitespace", false, "Insert whitespaces between atom name and residue name, between x and y, and between y and z.")
	flag.BoolVar(&c.includeHeader, "include_header", false, "Include pdb header in pqr file.")

	// System options
	flag.BoolVar(&c.version, "version", false, "Show program’s version number and exit.")
	flag.BoolVarP(&c.help, "help", "h", false, "Print help message and exit.")

}

// func (c *commandLine) JSON() string {
func (c *commandLine) JSON() map[string]interface{} {
	// var jsonStr string
	// var flagMap map[string]interface{}

	jsonMap := make(map[string]interface{})
	flagMap := make(map[string]interface{})

	// flag.visit(), adding flag name/value pairs to an interface object
	flag.Visit(func(f *flag.Flag) {
		if f.Name != "id" {
			flagMap[f.Name] = f.Value
		}
	})

	jsonMap["invoke_method"] = "cli"
	jsonMap["pdb_name"] = c.pdbFilename
	jsonMap["pqr_name"] = c.pqrFilename
	jsonMap["flags"] = flagMap

	// data, err := json.Marshal(jsonMap)
	// rest.CheckErr(err)

	// jsonStr = string(data)

	// return jsonStr

	return jsonMap
}

func (c *commandLine) PrintHelpMessage() {
	// var f *flag.Flag
	var flagArray []string

	fmt.Printf("This module takes a PDB file as input and performs optimizations before\n%s\n%s\n\n",
		"yielding a new PQR-style file in PQR_OUTPUT_PATH. If PDB_PATH is an ID it will",
		"automatically be obtained from the PDB archive.",
	)

	fmt.Printf("Options:\n")

	// System options
	flagArray = []string{"version", "help"}
	printHelpLine(flagArray, 2)
	fmt.Println()

	// Manditory options
	fmt.Println("  Manditory options:")
	flagArray = []string{"ff", "userff", "clean"}
	printHelpLine(flagArray, 4)
	fmt.Println()

	// General Options
	fmt.Println("  General options:")
	flagArray = []string{
		"apbs-input",
		"assign-only",
		"chain",
		"drop-water",
		"ffout",
		"ligand",
		"neutraln",
		"neutralc",
		"nodebump",
		"noopts",
		"typemap",
		"usernames",
		"verbose",
		"whitespace",
		"include_header",
	}
	printHelpLine(flagArray, 4)
	fmt.Println()

	// pH options:
	fmt.Println("  pH options:")
	flagArray = []string{"ph-calc-method", "with-ph"}
	printHelpLine(flagArray, 4)
	fmt.Println()

	// PDB2PKA method options
	fmt.Println("  PDB2PKA method options:")
	flagArray = []string{"pdb2pka-out", "pdb2pka-resume", "pdie", "sdie", "pairene"}
	printHelpLine(flagArray, 4)
	fmt.Println()

	// PROPKA method options
	fmt.Println("  PROPKA method options:")
	flagArray = []string{"propka-reference", "propka-verbose"}
	printHelpLine(flagArray, 4)

}

func printHelpLine(flagArray []string, indent int) {
	maxWidth := 24
	maxPadding := maxWidth - indent

	for _, name := range flagArray {
		f := flag.Lookup(name)
		if f.Shorthand != "" {
			reducedPadding := maxPadding - 4
			cliString := fmt.Sprintf("%s, %-*s", "-"+f.Shorthand, reducedPadding, "--"+name)
			fmt.Printf("%*s%s%s\n", indent, "", cliString, f.Usage)
			// fmt.Printf("%*s, %-18s%s\n", indent, "-"+f.Shorthand, "--"+f.Name, f.Usage)
			// fmt.Printf("  -%s, --%-%ds%s\n", f.Shorthand, f.Name, f.Usage)
		} else {
			switch argName := f.Name; argName {
			case "userff":
				name = fmt.Sprintf("%s=USER_FIELD_FILE\n%*s", argName, maxWidth, "")
			case "usernames":
				name = fmt.Sprintf("%s=USER_NAME_FILE\n%*s", argName, maxWidth, "")
			case "ph-calc-method":
				name = fmt.Sprintf("%s=PH_METHOD\n%*s", argName, maxWidth, "")
			case "with-ph":
				name = fmt.Sprintf("%s=PH\n%*s", argName, maxWidth, "")
			case "pdb2pka-out":
				name = fmt.Sprintf("%s=PDB2PKA_OUT\n%*s", argName, maxWidth, "")
			case "pdie":
				name = fmt.Sprintf("%s=PDB2PKA_PDIE\n%*s", argName, maxWidth, "")
			case "sdie":
				name = fmt.Sprintf("%s=PDB2PKA_SDIE\n%*s", argName, maxWidth, "")
			case "pairene":
				name = fmt.Sprintf("%s=PDB2PKA_PAIRENE\n%*s", argName, maxWidth, "")
			case "propka-reference":
				name = fmt.Sprintf("%s=PROPKA_REFERENCE\n%*s", argName, maxWidth, "")
				// default:
			}
			cliString := fmt.Sprintf("%-*s", maxPadding, "--"+name)
			fmt.Printf("%*s%s%s\n", indent, "", cliString, f.Usage)
		}

	}
}

func commandLineToForm(c commandLine) form {
	var obj form
	// form = &form{}

	return obj
}

// FormCLI : struct encapsulating the JSON format of the PDB2PQR form
type FormCLI struct {
	invokeMethod string                 `json:"invoke_ethod"`
	pdbName      string                 `json:"pdb_name"`
	pqrName      string                 `json:"pqr_name"`
	flags        map[string]interface{} `json:"flags"`
}

func main() {
	var apbsURL string
	var allInputFiles []string
	var Options commandLine
	// var helpFlag bool

	apbsURL = rest.GetInstallURL()
	println(apbsURL)
	Options.Init()

	Options.OptionsFlagSet = flag.NewFlagSet("Options:", flag.ExitOnError)
	Options.OptionsFlagSet.AddFlag(flag.Lookup("help"))
	// helpFlag = *flag.Bool("help", false, "Print help message and exit.")

	// jobid = "devTestPdb2pqr"

	flag.Parse()

	// Check version flag
	if Options.version {
		pdb2pqrVersion := os.Getenv("PDB2PQR_VERSION")
		if pdb2pqrVersion == "" {
			pdb2pqrVersion = "DEV"
		}
		fmt.Printf("pdb2pqr (Version %s)\n", pdb2pqrVersion)
		return
	} else if Options.help {
		// Check Help flag
		// rest.PrintUsageError("PDB2PQR", flag.PrintDefaults)
		rest.PrintUsageError("PDB2PQR", Options.PrintHelpMessage)
		return
	}

	// Check mandatory flags for valid input

	// Check optional flags for valid input

	// get input PDB filename and output PQR filename
	inputName := flag.Arg(0)
	outputName := flag.Arg(1)

	Options.pdbFilename = path.Base(inputName)
	Options.pqrFilename = path.Base(outputName)
	// fmt.Println(string(Options.JSON()))

	// if rest.File

	// create list of input files, upload to storage
	allInputFiles = append(allInputFiles, inputName)
	// TODO: add other input files to list (e.g. ligand, userff, etc)

	rest.UploadFilesToStorage(allInputFiles, Options.jobid)
	fmt.Println() // empty line
	// if Options.

	// Build submission form
	formObj := Options.JSON()

	// Start PDB2PQR workflow
	rest.StartWorkflow(Options.jobid, "pdb2pqr", formObj)

	// Wait for completion, get final status
	finalStatus := rest.WaitForExecutionPDB2PQR(Options.jobid)
	fmt.Printf("Job complete.\n\n")

	// Download output files
	fmt.Printf("Downloading output files:\n")
	for _, file := range finalStatus.Pdb2pqr.OutputFiles {
		fmt.Printf("  %s\n", path.Base(file))
		rest.DownloadFile(path.Base(file), Options.jobid)
	}
	fmt.Printf("Finished.\n")

	// Print apbs_output to stdout
	data, err := ioutil.ReadFile("pdb2pqr_stdout.txt")
	rest.CheckErr(err)
	os.Stdout.WriteString(string(data))

	// Print error output to stderr
	data, err = ioutil.ReadFile("pdb2pqr_stderr.txt")
	rest.CheckErr(err)
	os.Stderr.WriteString(string(data))

	// fmt.Println()
	// fmt.Println(allInputFiles, inputName, outputName)

	// fmt.Println(Options.jobid)
	// fmt.Println(Options.forcefield)
	// fmt.Println(Options.apbsInput)
	// flag.PrintDefaults()
}
