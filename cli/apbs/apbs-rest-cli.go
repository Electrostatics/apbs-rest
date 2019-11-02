package main

import (
	"bufio"
	"log"

	"io/ioutil"
	"os"
	"path"
	"strings"

	"github.com/Electrostatics/apbs-rest/cli/rest"
	flag "github.com/spf13/pflag"
)

type commandLine struct {
	jobid         string
	inputFilename string

	// System Options
	version bool
	help    bool
	debug   bool
}

// form structure for workflow submission
type form struct {
	Filename string `json:"filename"`
}

// ExtractReadFiles : extracts the input files specified in READ seciton
//                    of APBS input file
func ExtractReadFiles(inputContents string) []string {
	var fileNames []string
	readStart := false
	readEnd := false
	scanner := bufio.NewScanner(strings.NewReader(inputContents))

	for i := 0; scanner.Scan(); i++ {
		lineText := strings.TrimSpace(scanner.Text())
		splitLine := strings.Fields(lineText)

		for _, element := range splitLine {
			if strings.ToUpper(element) == "READ" {
				readStart = true
			} else if strings.ToUpper(element) == "END" {
				readEnd = true
			} else {
				fileNames = append(fileNames, element)
			}
			// Break from loop when we've exited READ section
			if readStart && readEnd {
				break
			}
		}
		// Since we've reached the end of the READ section, stop reading file
		if readStart && readEnd {
			break
		}
	}
	// removes the type of file/format from list (e.g. 'charge pqr')
	fileNames = fileNames[2:]

	// check that each file exists
	for _, name := range fileNames {
		if rest.FileExists(name) == false {
			panic("File '" + name + "' does not exist. Specified within READ block of input file")
		}
	}

	return fileNames
}

func main() {
	log.SetFlags(log.Flags() &^ (log.Ldate | log.Ltime))
	var Options commandLine

	// Define flags for the help text
	flag.StringVar(&Options.jobid, "id", "", "Specify custom job identifier for execution. Defaults to randomly generated ID.")
	flag.BoolVar(&Options.debug, "debug", false, "Print additional information to stdout.")
	flag.BoolVarP(&Options.help, "help", "h", false, "Print help message and exit.")
	// jobid = "devTest"

	// TODO: consider whether to print licensing flag from old binaries

	/**
	Check command line arguments
	*/
	flag.Parse()

	// If no --debug, send log output to /dev/null
	if !Options.debug {
		log.SetOutput(ioutil.Discard)
	}

	// Display help message when --help flag is specified
	if Options.help {
		rest.PrintUsageError("APBS", flag.PrintDefaults)
		return
	}

	// Retrieve job ID if none is specified
	if Options.jobid == "" {
		Options.jobid = rest.GetNewID()
	}

	if flag.NArg() < 1 {
		rest.PrintUsageError("APBS", flag.PrintDefaults, "Not enough arguments: APBS input file required")
		// panic("Not enough arguments: APBS input file required")
	} else {
		var jobid string
		var allInputFiles []string

		jobid = Options.jobid

		// verify inputfile's existence
		apbsFileName := flag.Arg(0)
		if rest.FileExists(apbsFileName) == false {
			panic("Input file '" + apbsFileName + "' does not exist")
		}

		// Read input file contents to string
		data, err := ioutil.ReadFile(apbsFileName)
		if err != nil {
			log.Print(err)
		}
		inputFileContents := string(data)

		readFileNames := ExtractReadFiles(inputFileContents)
		log.Println("File names extracted from", apbsFileName, ":\n", readFileNames)

		// Join input file and READ block files within same list
		allInputFiles = append(allInputFiles, apbsFileName)
		for _, name := range readFileNames {
			allInputFiles = append(allInputFiles, name)
		}

		log.Println() // empty line
		log.Println(jobid)

		// Upload input files to storage service
		rest.UploadFilesToStorage(allInputFiles, jobid)
		log.Println() // empty line

		// Build submission form
		formObj := &form{
			Filename: path.Base(apbsFileName)}

		// Start APBS workflow
		rest.StartWorkflow(jobid, "apbs", *formObj)

		// Wait for completion, get final status
		finalStatus := rest.WaitForExecution(jobid)
		log.Printf("Job complete.\n\n")

		// Download output files
		log.Printf("Downloading output files:\n")
		for _, file := range finalStatus.Apbs.OutputFiles {
			log.Printf("  %s\n", path.Base(file))
			rest.DownloadFile(path.Base(file), jobid)
		}
		log.Printf("Finished.\n")

		// Print apbs_output to stdout
		data, err = ioutil.ReadFile("apbs_stdout.txt")
		rest.CheckErr(err)
		os.Stdout.WriteString(string(data))

		// Print error output to stderr
		data, err = ioutil.ReadFile("apbs_stderr.txt")
		rest.CheckErr(err)
		os.Stderr.WriteString(string(data))

		// Cleanout job files from cluster and stdout/stderr from local
		rest.DeleteServerJobDirectory(jobid) // TODO: run this at exit if anything is uploaded
	}
}
