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
  pdb_name=$(ls *.pdb)
  userff_name=$(ls *.DAT)
  usernames_name=$(ls *.names)
  ligand_name=$(ls *.mol2)

  output_basename=$2

  # Record the end time for the job
  date +%s.%N  | xargs printf '%.*f\n' 2 > pdb2pqr_end_time

  echo ''
  echo 'Writing pdb2pqr_status'

  # Write to the pdb2pqr_status
  echo 'complete' >> ${task_name}_status
  
  # Write the PDB input file
  if [ $pdb_name != '' ]
  then
    echo $JOB_ID/$pdb_name >> ${task_name}_status
  fi

  # Write the User Forcefield input file
  if [ $userff_name != '' ]
  then
    echo $JOB_ID/$userff_name >> ${task_name}_status
  fi
  
  # Write the User Names input file
  if [ $usernames_name != '' ]
  then
    echo $JOB_ID/$usernames_name >> ${task_name}_status
  fi

  # Write the Ligand input file
  if [ $ligand_name != '' ]
  then
    echo $JOB_ID/$ligand_name >> ${task_name}_status
  fi

  # Write the output files
  for file in $output_basename*
  do
    echo $JOB_ID/${file} >> ${task_name}_status
    echo $JOB_ID/${file} >> ${task_name}_output_files
  done

  if [ $output_basename = $JOB_ID ] # if outputname is assigned by jobid
  then
    if [ -f apbsinput.in ]
    then
      cp *.in apbsinput.in # might not be needed anymore. Need to investigate
      echo apbsinput.in is found. Sending to output_files
      echo $JOB_ID/apbsinput.in >> ${task_name}_status
      echo $JOB_ID/apbsinput.in >> ${task_name}_output_files
    fi

  else # if outputname is defined by client
    if [ -f $output_basename.in ]
    then
      echo $output_basename is found. Sending to output_files
      echo $JOB_ID/$output_basename.in >> ${task_name}_status
      echo $JOB_ID/$output_basename.in >> ${task_name}_output_files
    fi
  fi


  echo $JOB_ID/pdb2pqr_stdout.txt >> ${task_name}_status
  echo $JOB_ID/pdb2pqr_stderr.txt >> ${task_name}_status
  echo $JOB_ID/pdb2pqr_stdout.txt >> ${task_name}_output_files
  echo $JOB_ID/pdb2pqr_stderr.txt >> ${task_name}_output_files

  
elif [ ${task_name} = 'apbs' ]
then
  cp *.in apbsinput.in # might not be needed anymore. Need to investigate
  pqr_name=$(ls *.pqr)
  # dx_name=*.dx

  # Record the end time for the job
  date +%s.%N  | xargs printf '%.*f\n' 2 > apbs_end_time 

  echo ''
  echo 'Writing apbs_status'

  echo 'complete'           >> ${task_name}_status

  # Record the input files
  echo $JOB_ID/apbsinput.in >> ${task_name}_status
  echo $JOB_ID/$pqr_name    >> ${task_name}_status

  # Record the output files
  echo $JOB_ID/io.mc        >> ${task_name}_status
  echo $JOB_ID/io.mc        >> ${task_name}_output_files

  for file in *.dx
  do
    echo $JOB_ID/${file} >> ${task_name}_status
    echo $JOB_ID/${file} >> ${task_name}_output_files
  done

  echo $JOB_ID/apbs_stdout.txt >> ${task_name}_status
  echo $JOB_ID/apbs_stderr.txt >> ${task_name}_status
  echo $JOB_ID/apbs_stdout.txt >> ${task_name}_output_files
  echo $JOB_ID/apbs_stderr.txt >> ${task_name}_output_files
fi

cd $cur_dir