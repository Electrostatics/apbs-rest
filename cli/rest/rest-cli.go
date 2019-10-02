package rest

import (
	"bufio"
	"encoding/json"

	// "flag"
	"fmt"
	"io"
	"io/ioutil"
	"net/http"
	"os"
	"path"
	"strings"
	"time"
)

// APBSUrl : Url for the APBS-Rest service
const APBSUrl = "http://apbs.127.0.0.1.xip.io"

// DownloadSuccessCode : HTTP status for successful download
const DownloadSuccessCode = 200

// UploadSuccessCode : HTTP status for successful upload
const UploadSuccessCode = 201

// WorkflowSuccessCode : HTTP status for successful workflow submission
const WorkflowSuccessCode = 202

// JobStatus : structure of the same-named JSON object
type JobStatus struct {
	JobID   string `json:"jobid"`
	JobType string `json:"jobtype"`
	Apbs    struct {
		Status      string   `json:"status"`
		StartTime   float32  `json:"startTime"`
		EndTime     float32  `json:"endTime"`
		Files       []string `json:"files"`
		InputFiles  []string `json:"inputFiles"`
		OutputFiles []string `json:"outputFiles"`
	} `json:"apbs"`
}

// JobStatusPDB2PQR : structure of the same-named JSON object
type JobStatusPDB2PQR struct {
	JobID   string `json:"jobid"`
	JobType string `json:"jobtype"`
	Pdb2pqr struct {
		Status      string   `json:"status"`
		StartTime   float32  `json:"startTime"`
		EndTime     float32  `json:"endTime"`
		Files       []string `json:"files"`
		InputFiles  []string `json:"inputFiles"`
		OutputFiles []string `json:"outputFiles"`
	} `json:"pdb2pqr"`
}

// Workflow : structure used to submit a workflow request
type Workflow struct {
	Workflow string      `json:"workflow"`
	Form     interface{} `json:"form"`
}

// GetInstallURL : retrieves the address of the local APBS-REST installation
func GetInstallURL() string {
	url := "apbs.127.0.0.1.xip.io"

	// prepend 'http://' to satisfy protocol requirement
	url = fmt.Sprintf("http://%s", url)

	return url
}

// CheckErr : performs obligatory error check
func CheckErr(err error) {
	if err != nil {
		panic(err)
	}
}

// PrintUsageError : prints usage error given incorrect invocation
// func PrintUsageError(program string, message string) {
func PrintUsageError(programName string, printOptions func(), message ...string) {
	programName = strings.ToLower(programName)
	if programName == "apbs" {
		os.Stderr.WriteString("USAGE: apbs [--options] <filename>.in\n\n")
	} else if programName == "pdb2pqr" {
		os.Stderr.WriteString("USAGE: pdb2pqr [--options] --ff=<forcefield> <input-path> <output-path>\n\n")
	}

	// if message != "" {
	if len(message) > 0 {
		// errString := fmt.Sprintf("%s\n", message)
		var errString string
		for i, segment := range message {
			if i > 0 {
				errString = fmt.Sprintf("%s %s", errString, segment)
			} else {
				errString = fmt.Sprintf("%s", segment)
			}
		}
		errString = fmt.Sprintf("%s\n", errString)

		os.Stderr.WriteString(errString)
	}

	// Print default help options, independent of flag implementation package
	printOptions()

}

// GetNewID : obtains a newly generated id from APBS services
func GetNewID() string {
	idServiceURL := APBSUrl + "/id/"

	// Get new job ID
	resp, err := http.Get(idServiceURL)
	CheckErr(err)
	defer resp.Body.Close()

	// Decode id JSON reponse
	//   referenced from: https://blog.golang.org/json-and-go
	body, err := ioutil.ReadAll(resp.Body)
	CheckErr(err)

	var rawData interface{}
	err = json.Unmarshal(body, &rawData)
	CheckErr(err)

	jsonObj := rawData.(map[string]interface{})
	// fmt.Println(jsonObj["job_id"])

	return jsonObj["job_id"].(string)
}

// FileExists : checks if file exists and that it is not a directory
// snippet extracted from: https://golangcode.com/check-if-a-file-exists/
func FileExists(name string) bool {
	info, err := os.Stat(name)
	if os.IsNotExist(err) {
		return false
	}
	return !info.IsDir()
}

// SendSingleFile : uploads a single file to APBS storage service
func SendSingleFile(fileName string, objectName string) (string, int) {
	storageURL := fmt.Sprintf("%s/storage/%s", APBSUrl, objectName)

	fin, err := os.Open(fileName)
	defer fin.Close()
	CheckErr(err)

	buf := bufio.NewReader(fin)
	resp, err := http.Post(storageURL, "application/form-data", buf)
	CheckErr(err)

	contentBytes, err := ioutil.ReadAll(resp.Body)
	CheckErr(err)

	content := string(contentBytes)
	status := resp.StatusCode
	return content, status
}

// UploadFilesToStorage : upload files to APBS storage service
func UploadFilesToStorage(fileList []string, jobid string) {
	storageURL := APBSUrl + "/storage/"

	fmt.Printf("Sending files to storage (id: %s):\n", jobid)
	for _, name := range fileList {
		fmt.Printf("  %s", name)
		objectName := fmt.Sprintf("%s/%s", jobid, path.Base(name))
		respContent, respCode := SendSingleFile(name, objectName)

		// Raise error if returned status code isn't success
		if respCode != UploadSuccessCode {
			message := fmt.Sprintf("Error in uploading %s. Response code: %d", name, respCode)
			panic(message)
		}
		fmt.Printf(" ...%s\n", respContent)
	}
	fmt.Println("Uploading finished. Files sent to", storageURL)
}

// StartWorkflow : send the request to start the APBS workflow job
// func StartWorkflow(infileName string, jobid string, workflowType string, formObj interface{}) {
func StartWorkflow(jobid string, workflowType string, formObj interface{}) {
	// type workflow struct {
	// 	Workflow string `json:"workflow"`
	// 	Form     form   `json:"form"`
	// }

	workflowURL := fmt.Sprintf("%s/workflow/%s/%s", APBSUrl, jobid, workflowType)
	statusURL := fmt.Sprintf("%s/jobstatus?jobtype=%s&jobid=%s", APBSUrl, workflowType, jobid)

	// prepare
	// infileObject := fmt.Sprintf("%s/%s", jobid, path.Base(infileName))

	workflowObj := &Workflow{
		// workflowObj := &workflow{
		Workflow: workflowType,
		Form:     formObj}

	jsonBytes, err := json.Marshal(workflowObj)
	CheckErr(err)
	jsonString := string(jsonBytes)
	fmt.Println(jsonString)

	fmt.Printf("Requesting workflow execution (id: %s)\n", jobid)

	resp, err := http.Post(workflowURL, "application/json", strings.NewReader(jsonString))
	CheckErr(err)

	// Raise error if returned status code isn't success
	if resp.StatusCode != WorkflowSuccessCode {
		message := fmt.Sprintf("Error in submitting APBS workflow. Response code: %d", resp.StatusCode)
		panic(message)
	}

	fmt.Printf("  Job submitted: %s\n", workflowURL)
	fmt.Printf("  View status:   %s\n", statusURL)
}

// WaitForExecution : waits for execution to complete for job, returns end status of job
// func WaitForExecution(jobid string) []string {
func WaitForExecution(jobid string) JobStatus {
	var returnedStatus JobStatus
	// wait := true
	wait := false
	workflowURL := fmt.Sprintf("%s/workflow/%s/apbs?wait=%t", APBSUrl, jobid, wait)

	fmt.Println()
	fmt.Printf("Waiting for job to complete.\n")

	if wait {
		resp, err := http.Get(workflowURL)
		time.Sleep(1 * time.Second)
		resp, err = http.Get(workflowURL)
		CheckErr(err)

		body, err := ioutil.ReadAll(resp.Body)
		CheckErr(err)

		println(workflowURL)
		println(string(body))

		err = json.Unmarshal(body, &returnedStatus)
		CheckErr(err)

	} else {
		jobState := "nil"
		counter := 0
		for jobState != "complete" {
			fmt.Printf("Counter: %d", counter)

			resp, err := http.Get(workflowURL)
			body, err := ioutil.ReadAll(resp.Body)
			CheckErr(err)
			err = json.Unmarshal(body, &returnedStatus)
			CheckErr(err)
			jobState = returnedStatus.Apbs.Status

			time.Sleep(time.Second)
			fmt.Printf("\r")
			counter++
		}
		fmt.Println()
	}

	return returnedStatus
}

// WaitForExecutionPDB2PQR : waits for execution to complete for job, returns end status of job
// func WaitForExecution(jobid string) []string {
func WaitForExecutionPDB2PQR(jobid string) JobStatusPDB2PQR {
	wait := true
	workflowURL := fmt.Sprintf("%s/workflow/%s/pdb2pqr?wait=%t", APBSUrl, jobid, wait)

	fmt.Println()
	fmt.Printf("Waiting for job to complete.\n")

	resp, err := http.Get(workflowURL)
	time.Sleep(time.Second)
	resp, err = http.Get(workflowURL)
	CheckErr(err)

	body, err := ioutil.ReadAll(resp.Body)
	CheckErr(err)

	println(workflowURL)
	println(string(body))

	var returnedStatus JobStatusPDB2PQR
	err = json.Unmarshal(body, &returnedStatus)
	CheckErr(err)

	return returnedStatus
}

// DownloadFile : download a file given a specified filename and jobid
func DownloadFile(fileName string, jobid string) {
	downloadURL := fmt.Sprintf("%s/storage/%s/%s", APBSUrl, jobid, fileName)

	// Get file contents from storage service
	resp, err := http.Get(downloadURL)
	CheckErr(err)
	defer resp.Body.Close()

	// Raise error if returned status code isn't success
	if resp.StatusCode != DownloadSuccessCode {
		message := fmt.Sprintf("Error in downloading %s. Response code: %d", fileName, resp.StatusCode)
		panic(message)
	}

	// Open/create file
	fout, err := os.Create(fileName)
	CheckErr(err)
	defer fout.Close()

	// Write and save contents
	_, err = io.Copy(fout, resp.Body)
	CheckErr(err)

}
