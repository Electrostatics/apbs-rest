#!/bin/sh

# for file in _upload/*
cur_dir=$(pwd)
task_name=$1
upload_dir=/app/_upload

# mkdir _upload
cp * $upload_dir

cd $upload_dir

rm $upload_dir/${task_name}_status

if [ ${task_name} = 'pdb2pqr' ]
then
  cp *.in apbsinput.in

  pdb_name=$(ls *.pdb)
  output_basename=$2

  # Record the end time for the job
  date +%s.%N  | xargs printf '%.*f\n' 2 > pdb2pqr_end_time

  echo ''
  echo 'Writing pdb2pqr_status'

  # Write to the pdb2pqr_status
  echo 'complete'        >> ${task_name}_status
  echo $JOB_ID/$pdb_name >> ${task_name}_status
  for file in $output_basename*
  do
    echo $JOB_ID/${file} >> ${task_name}_status
  done
  
elif [ ${task_name} = 'apbs' ]
then
  pqr_name=$(ls *.pqr)
  # dx_name=*.dx

  # Record the end time for the job
  date +%s.%N  | xargs printf '%.*f\n' 2 > apbs_end_time 

  echo ''
  echo 'Writing apbs_status'

  echo 'complete'           >> ${task_name}_status
  echo $JOB_ID/apbsinput.in >> ${task_name}_status
  echo $JOB_ID/$pqr_name    >> ${task_name}_status
  echo $JOB_ID/io.mc        >> ${task_name}_status
  
  for file in *.dx
  do
    echo $JOB_ID/${file} >> ${task_name}_status
  done

  echo $JOB_ID/apbs_stdout.txt >> ${task_name}_status
  echo $JOB_ID/apbs_stderr.txt >> ${task_name}_status
fi

cd $cur_dir