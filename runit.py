#!/usr/bin/env python
# -*- python -*-
import os, sys
import json
from datetime import datetime

import create_runscript 

#####################
#
# Edit these values
#
#####################

### IMPORTANT: uncomment the type of run this is
run_type = "control"
#run_type = "experiment"

# This code creates a json file that lists the log file to use in the plots.  This flag controls the ability to
# add this set of log files to the existing experiment file lists or should this set be the only files listed under the 
# experiment sections.
add_to_experiment_list = True

cm1_code_base = '/glade/scratch/mickelso/CM1/CM1/'
project_code = 'NTDD0004'
queue = 'casper'
machine = 'casper'
namelist_input_list = [
    'namelist.asd03-verify.input'
#    'namelist.sas.input',
#    'namelist.asd04-128x512.input'
]
exe_list = {
#'cm1-mpi.exe': {'args': 'FC=ifort USE_MPI=true USE_OPENMP=false USE_DOUBLE=false USE_OPENACC=false DEBUG=false',
#                          'mpi':True,
#                          'nodes':1,
#                          'ncpus':36,
#                          'mpiprocs':36,
#                          'ngpus':0,
#                          'walltime':'00:30:00'
#                         }
#'cm1-openacc.exe': {'args': 'FC=nvfortran USE_MPI=false USE_OPENMP=false USE_DOUBLE=false USE_OPENACC=true DEBUG=false',
#                          'mpi':False,
#                          'nodes':1,
#                          'ncpus':1,
#                          'mpiprocs':1,
#                          'ngpus':1,
#                          'walltime':'00:30:00'
#                         },
'cm1-mpi-openacc.exe': {'args':'FC=nvfortran USE_MPI=true USE_OPENMP=false USE_DOUBLE=false USE_OPENACC=true DEBUG=false',
                          'mpi':True,
                          'nodes':1,
                          'ncpus':2,
                          'mpiprocs':2,
                          'ngpus':2,
                          'walltime':'00:30:00'                                
                         }
}

########################
#
# End edittable section
#
########################

cwd = os.getcwd()

# generate time stamp information
verNum_temp = datetime.now().strftime("%Y_%m_%d-%I:%M:%S")
verNum = verNum_temp.replace(":","_")
json_file = "logs/files.json"
if not os.path.exists(cwd+"/logs"):
    os.makedirs(cwd+"/logs")
if not os.path.exists(cwd+"/run_scripts"):
    os.makedirs(cwd+"/run_scripts")

err = 0
problem_builds = []
successful_builds = []

for exe in exe_list:
    # get the Fortran compiler and OpenACC information
    args_list = exe_list[exe]['args']
    args_dict = dict(x.split("=") for x in args_list.split(" "))   
    FC_info = args_dict['FC'].lower()
    OpenACC_info = args_dict['USE_OPENACC'].lower()
    if  OpenACC_info:
        HW = "GPU"
    else:
        HW = "CPU"

    # change to the src directory to build 
    print('\n\n\n\n\n\n')
    print('############################################')
    print('')
    print('   Building code in '+cm1_code_base + '/src/')
    print('')
    print('############################################')
    os.chdir(cm1_code_base + "/src/")
    # load the modules based on compiler and machine
    machine=machine.lower()
    if FC_info == "ifort":
        if machine == "casper":
            module_load="module purge ; module load ncarenv/1.3 intel/19.1.1 openmpi/4.1.1 netcdf/4.8.1" 
        elif machine == "cheyenne":
            module_load="module purge ; module load ncarenv/1.3 intel/19.1.1 mpt/2.22 netcdf/4.8.1" 
        else:
            print("Non-NCAR machine, so no module changes will be made!")
    elif FC_info == "pgf90":
        if machine == "casper":
            if OpenACC_info:
                module_load="module purge ; module load ncarenv/1.3 pgi/20.4 openmpi/4.1.1 netcdf/4.7.4 cuda/11.4.0"
            else:
                module_load="module purge ; module load ncarenv/1.3 pgi/20.4 openmpi/4.1.1 netcdf/4.7.4"
        else:
            print("Not Casper, so no module changes will be made!")
    elif FC_info == "nvfortran":
        if machine == "casper":
            if OpenACC_info:
                module_load="module purge ; module load ncarenv/1.3 nvhpc/22.2 openmpi/4.1.1 netcdf/4.8.1 cuda/11.4.0"
            else:
                module_load="module purge ; module load ncarenv/1.3 nvhpc/22.2 openmpi/4.1.1 netcdf/4.8.1"
        else:
            print("Not Casper, so no module changes will be made!")
    else:
        sys.exit(FC_info + " is provided but only ifort, pgf90 and nvfortran are supported!")

    err = os.system("make clean")
    err = os.system("source /etc/profile.d/modules.sh ; " + module_load + " ; make -j 4 " + exe_list[exe]['args'])
    err = os.system("mv ../run/cm1.exe ../run/" + exe)
    if err != 0:
        print("ERROR: Problem while building")
        problem_builds.append(exe)
    else:
        print("Success!!!")
        successful_builds.append(exe)

        for namelist_input in namelist_input_list:
            # create a log file name
            # set version number to a time stamp
            # do not edit log_fn_base as it will not put control/experiment runs into the same pair
            log_fn_base = exe + "." + namelist_input
            log_fn = cwd + '/logs/' + log_fn_base + "." + machine + "." + HW + "." + FC_info + "." + verNum + '.log'

            print('############################################')
            print('')
            print('   Running '+cm1_code_base + '/run/'+exe)
            print('   Output will be piped to '+log_fn)
            print('')
            print('############################################')

            # set some variables for this setup
            run_dir = cm1_code_base + "/run/"
            run_script = cwd+'/run_scripts/'+os.path.basename(log_fn)+".submit.csh" 

            # create the run script to submit to the queue    
            create_runscript.create_runscript(exe, exe_list[exe], project_code, queue, module_load, 
                                              cwd, run_dir, log_fn, run_script, namelist_input)

            # submit the run script to the queue
            err = os.system("qsub "+run_script)
            if err != 0:
                print("ERROR: Problem submitting job to the queue")
            else:
                print("Success!!! Job is in the queue.")

            # change back to this scripts directory
            os.chdir(cwd)

            #########################################
            #
            # Update the json file with new log file
            #
            #########################################

            # Read the json file into memory in order to add the new file to the list  
            # If it doesn't exist, create an empty dictionary.
            if os.path.exists(json_file):
                with open(json_file) as f:
                    fns_raw = f.read()
                fns = json.loads(fns_raw)
            else:
                fns = {}
            if log_fn_base not in fns.keys():
                 fns[log_fn_base] = {"experiments":[], "control":""}
            if run_type is "experiment":
                if add_to_experiment_list:
                    fns[log_fn_base]['experiments'].append(log_fn)
                else:
                    fns[log_fn_base]['experiments'] = [log_fn]
            if run_type is "control":
                fns[log_fn_base]['control'] = log_fn
            with open(json_file, 'w') as f:
                json.dump(fns, f, indent=4)

print("============================================")
print("BUILD SUMMARY")
print("Successful builds:")
for b in successful_builds:
    print(b)
print("Unsuccessful builds:")
for b in problem_builds:
    print(b)
