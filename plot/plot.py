#! /usr/bin/env python

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import json
import numpy as np
import os
import argparse
from collections import OrderedDict

# constants
threshold = 1.0e-6

def parse_it(log_file):

    # flag to indicate if run finished okay
    run_completed = False

    # parse the log file
    info = {
              'stats':{},
              'metrics':{},
              'performance':{},
              'total_time':''
    }

    # boolean to indicate that we're in the timing section of the file in order to collect those values
    in_timing_section = False

    #  Grep for these strings in the files specified within the json file
    #  in order to verify correctness
    info['metrics'] = {
        'LWP (g/m2)': [],
        'cloud fraction (%)': [],
        'max w variance (m2/s2)': [],
        'preciptation rate (mm/day)':[]
    }

    # open the log file and pull out stat, metric, and timing information
    with open(log_file) as cfile:
        for line in cfile:
            # stat stuff
            if "stat::" in line:
                split = line.strip().replace("stat::","").split(':')
                #print(split)
                if split[0].strip() in info['stats'].keys():
                    info['stats'][split[0].strip()].append(split[1].split()[0].strip())
                else:
                    info['stats'][split[0].strip()] = [split[1].split()[0].strip()]
                if len(split) > 2:
                    if split[1].split()[-1].strip() in info['stats'].keys():
                        info['stats'][split[1].split()[-1].strip()].append(split[2].split()[0].strip())
                    else:
                        info['stats'][split[1].split()[-1].strip()] = [split[2].split()[0].strip()]
            # metric stuff
            elif "Metric:" in line:
               key = line.split('Metric:')[-1].strip().split('=')[0].strip()
               value = line.split()[-1]
               if key in info['metrics'].keys():
                   info['metrics'][key].append(float(value))               
            # performance and total time collection
            elif in_timing_section and ':' in line and len(line.split())==4 and 'Warning' not in line:
                split = line.split()
                key = split[0].strip()
                value = split[-1].strip().replace("%","")
                info['performance'][key] = value 
            elif 'Total time:' in line:
                 info['total_time'] = line.split()[-1].strip()
                 in_timing_section = True
            elif 'Program terminated normally' in line:
                run_completed = True

    return info, run_completed


def performance_plot(control, Cfname, experiment, f, save_plot):

    # combine low values
    low = 2.0

    # set up figure
    fig1, ax1 = plt.subplots(len(experiment.keys())+1,figsize=(15,15))

    # control
    Ctimings = control['performance'] 
    Cnew_timings = {'other':0}
    for k in Ctimings.keys():
        if float(Ctimings[k]) >= low:
            Cnew_timings[k] = float(Ctimings[k])
        else:
            Cnew_timings['other'] += float(Ctimings[k])
    ax1[0].pie(Cnew_timings.values(), labels=Cnew_timings.keys(), autopct='%1.1f%%')
    Ctitle = title = Cfname+"\n Total Time: "+control['total_time']+" (seconds)"
    ax1[0].set_title(Ctitle,fontsize=10)

    #experiment
    for i,e in enumerate(experiment.keys()):
        Etimings = experiment[e]['performance']
        Enew_timings = {'other':0}
        for k in Etimings.keys():
            if float(Etimings[k]) >= low:
                Enew_timings[k] = float(Etimings[k])
            else:
                Enew_timings['other'] += float(Etimings[k])

        ax1[i+1].pie(Enew_timings.values(), labels=Enew_timings.keys(), autopct='%1.1f%%')
        Etitle = os.path.basename(e)+"\n Total Time: "+experiment[e]['total_time']+" (seconds)"
        ax1[i+1].set_title(Etitle,fontsize=10)
    
    if save_plot:
        plt.savefig(f+'-performance.png')
    else:
        plt.show()

def line_info(_plt, Cvalues, Evalues, label):
        colors = []
        for e in Evalues:
            sub = []
            if (len(Cvalues) != len(Evalues[e]['metrics'][label])):
                print("The number of values to compare for label '"+label+"' are different between the control and experiment and the difference cannot be plotted.")
            else:
                for i in range(len(Cvalues)):
                    if (max(abs(Evalues[e]['metrics'][label][i]),abs(Cvalues[i])) != 0):
                        sub.append(abs(Evalues[e]['metrics'][label][i]-Cvalues[i])/max(abs(Evalues[e]['metrics'][label][i]),abs(Cvalues[i])))
                    else: #both are zero
                        sub.append(0.0)
                #colors.append(_plt.plot(sub))
                _plt.plot(sub,label=os.path.basename(e))
        _plt.set_xlabel('time (min)')
        _plt.set_ylabel(label)
        _plt.grid(linestyle='--')
        _plt.legend()
        return colors


def metric_plots(Cvalues, Evalues, f, save_plot):

    fig, ((pl1, pl2), (pl3,pl4)) = plt.subplots(2, 2, figsize=(12, 10))
    plts = [pl1, pl2, pl3, pl4]

    for i,label in enumerate(Cvalues.keys()):
        colors = line_info(plts[i], Cvalues[label], Evalues, label)

    plt.subplots_adjust(bottom=0.25)
    fig.suptitle("The relative differences in the Metric Values |(exp-ctrl)|/max(|exp|,|ctrl|)\n"+f)

    if save_plot:
        plt.savefig(f+'-metric.png') 
    else:
        plt.show()


def compare_stat_values(Cvalues, Evalues):

    ok = 0
    fail = 0        

    diff = {}

    if len(Cvalues) != len(Evalues):
        print("============================================")
        print("There is a mismatch in the amount of ccomparisons between the experiment v. control.  Doulble check that both runs completed and that they ran for the same number of timesteps.")
    else:
        for v in Cvalues.keys():
            if Cvalues[v] != Evalues[v]:
                #print("\nDIFFERENCE IN VARIABLE "+v)
                #print("Control values: ")
                #print(Cvalues[v])
                #print("Experiment values:")
                #print(Evalues[v])
                rd = []
                flag = False
                for i in range(0,len(Cvalues[v])):
                    if (max(abs(float(Evalues[v][i])),abs(float(Cvalues[v][i]))) != 0):
                        value = (abs(float(Evalues[v][i])-float(Cvalues[v][i])))/max(abs(float(Evalues[v][i])),abs(float(Cvalues[v][i])))
                        rd.append(value)
                        if value > threshold:
                            flag = True
                    else: #both are zero
                        rd.append(0.0)
                if flag:
                    print("\nRELATIVE DIFFERENCE IN VARIABLE "+v+" : |(exp-ctrl)|/max(|exp|,|ctrl|)")
                    print(rd)
                    diff[v] = rd
                    fail+=1
            else:
                print("\nNO DIFFERENCE IN VARIABLE "+v)
                ok+=1

        # Print the answer summary for this comparison
        print("============================================")
        print(str(ok)+" stat variables are ok.")
        print(str(fail)+" stat variables show a difference.")
    print("\n\n")
#    plt.legend(diff.keys())
#    plt.plot(diff.values())
#    plt.show()

    return ok,fail


def read_logs(json_file, save_plot):

    run_completed = {}

    # get log names that contain the values to plot
    with open(json_file) as f:
        fns_raw = f.read()
    fns = json.loads(fns_raw)
   
    total_ok = 0
    total_fail = 0
 
    # loop through the different sets of log files
    for f in sorted(fns.keys()):

        print("Working on the log files under: "+f)
        print("Using control file:"+fns[f]['control'])
        
        # parse the control file
        control,run_completed[fns[f]['control']] = parse_it(fns[f]['control'])
        # parse the experiment file(s)
        experiment={}
        for i,e in enumerate(fns[f]['experiments']):
            experiment[e],run_completed[fns[f]['experiments'][i]] = parse_it(fns[f]['experiments'][i])

        # compare this against the control
        for e in experiment:
            print("============================================")
            print("Summary for "+fns[f]['control']+" compared to "+os.path.basename(e))
            ok,fail = compare_stat_values(control['stats'], experiment[e]['stats'])
            total_ok = total_ok+ok
            total_fail = total_fail+fail

        # print and plot performance
        performance_plot(control, os.path.basename(fns[f]['control']),
                         experiment, f, save_plot)

        # create metric plots
        metric_plots(control['metrics'], experiment, f, save_plot)


    # Print a summary across all comparisons
    print("============================================")
    print("Summary for all stat comparisons")
    print(str(total_ok)+" stat variables are ok.")
    print(str(total_fail)+" stat variables show a difference.") 
    print("\n\n")

    # Print summary of job completion status
    print('\n')
    print("============================================")
    print("Did the run finish successfully?")
    for k in run_completed:
        print(k+": "+str(run_completed[k]))



def parseArguments():

    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--json", help="json input file that list the log files to use in analysis.", type=str, default="../logs/files.json")
    parser.add_argument("-s", "--save", help="True/False to save plot figures as png files.", type=str, default='False')
    args = parser.parse_args()

    return args   

if __name__ == '__main__':

    # read in arguments
    args = parseArguments()
    save_plot = args.__dict__['save']
    if save_plot.upper() == 'TRUE':
         b_save_plot = True
    else:
         b_save_plot = False

    read_logs(args.__dict__['json'], b_save_plot)


