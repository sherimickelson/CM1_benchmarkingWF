# Running this code on NCAR's Casper cluster
You'll want to make sure that you have loaded Python and some basic Python libraries before you run this code.
First, make sure you have conda loaded in your environment.  If it is not there, execute
`module load conda`
Next, execute
`conda activate npl`
Then you should be ready to run the following scripts.

# CM1 Benchmarking Workflow
This work was designed to be a testing framework used to verify changes that are made to the CM1 code, specifically for the GPU branch of the code. 

This code has the ability to:
- Build the CM1 code with multiple configurations
- Run each built executable with multiple namelist files
- Compare output log files and notes differences in answers within a specified tolerence
- Plots answer changes along simulation time
- Plots the proportion of time spent in the code within a pie chart


## Instructions
### Part 1:
This part will build the CM1 code and submit jobs to the queue.
1. Open the `runit` script found in the top level directory.
2. Go to the section `Edit these values` and make any needed modification in that section.
3. Execute the `runit` script.
The code will then loop through the `exe_list` and build all of the executables.  After each build, the code loops through the `namelist_input_list` 
and submits a job the queue for each namelist the user wants to run.

### Part 2:
This part will examine the log files and compare answers and print the differences, create a timeseries of the differences, and plot timing statistics.  This part should be ran once all of the execuatables have run in Part 1.

(Optional step) Open up the file `logs/files.json` and examine the contents.  The different sections listed here show the comparisons that will be made.  Each section contains a key name that contains the executable and namelist names.  Under this is a list of `experiments` logs that will each be compared against the `control` log that is listed.  This file should be filled in automatically based on what is selected in Part 1 and it is amended to as additional log files are created.  It may also be modified by hand if the user would like to customize the comparison that they would like to see.
1. Run `python plot.py`.
