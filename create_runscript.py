from jinja2 import Template
import os

def create_runscript(exe, params, project_code, queue, script_dir, run_dir, log_file, run_script, namelist_input):

    if params['mpi'] is True:
        mpi = 'mpirun -n '+str(params['mpiprocs'])
    else:
        mpi = ''

    if (int(params['ngpus']) > 0):
        t = Template(
"""#!/bin/bash -l
#PBS -N cm1
#PBS -l select={{ nodes }}:ncpus={{ ncpus }}:mpiprocs={{ mpirpcs }}:ngpus={{ ngpus }}
#PBS -l gpu_type=v100
#PBS -l walltime={{ walltime }}
#PBS -j oe
#PBS -A {{ project_code }}
#PBS -q {{ queue }}

module purge
module load ncarenv/1.3 nvhpc/21.11 openmpi netcdf

export LD_LIBRARY_PATH=${NCAR_ROOT_CUDA}/lib64:${LD_LIBRARY_PATH}
export UCX_MEMTYPE_CACHE=n
export UCX_TLS=rc,sm,cuda_copy,cuda_ipc
export OMPI_MCA_pml=ucx
export OMPI_MCA_btl=self,vader,tcp,smcuda
export UCX_RNDV_SCHEME=put_zcopy
export UCX_RNDV_THRESH=2

cd {{ run_dir }}

{{ mpi }} ./{{ exe }} --namelist {{namelist_input}} >&  {{ log_file }}
"""
                )
    else:
        t = Template(
"""#!/bin/bash -l
#PBS -N cm1
#PBS -l select={{ nodes }}:ncpus={{ ncpus }}:mpiprocs={{ mpirpcs }}
#PBS -l walltime={{ walltime }}
#PBS -j oe
#PBS -A {{ project_code }}
#PBS -q casper

module purge
module load ncarenv/1.3 nvhpc/21.11 openmpi netcdf

cd {{ run_dir }}

{{ mpi }} ./{{ exe }} --namelist {{namelist_input}} >&  {{ log_file }}
"""
                )

    output = t.render(
              nodes = params['nodes'],
              ncpus = params['ncpus'],
              mpirpcs = params['mpiprocs'],
              ngpus = params['ngpus'],
              walltime = params['walltime'],
              project_code = project_code, 
              queue = queue,
              run_dir = run_dir,
              mpi = mpi,
              exe = exe,
              namelist_input = namelist_input,
              script_dir = script_dir,
              log_file = log_file 
            )

    with open(run_script, 'w') as f:
        f.write(output)


