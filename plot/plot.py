import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import json
import numpy as np
from collections import OrderedDict

def parse_it(log_file):

    # parse the log file
    info = {
              'stat':{},
              'metric':{},
              'performance':{}
    }
    with open(log_file) as cfile:
        for line in cfile:
            if "stat::" in line:
                split = line.strip().replace("stat::","").split(':')
                #print(split)
                if split[0].strip() in info['stat'].keys():
                    info['stat'][split[0].strip()].append(split[1].split()[0].strip())
                else:
                    info['stat'][split[0].strip()] = [split[1].split()[0].strip()]
                if len(split) > 2:
                    if split[1].split()[-1].strip() in info['stat'].keys():
                        info['stat'][split[1].split()[-1].strip()].append(split[2].split()[0].strip())
                    else:
                        info['stat'][split[1].split()[-1].strip()] = [split[2].split()[0].strip()]
#    for v in info['stat'].keys():
#        print("\n"+log_file+"\n"+v+": size "+str(len(info['stat'][v])))
#        print(info['stat'][v])


    return info


def read_logs(json_file):
    #  Grep for these strings in the files specified within the json file
    # Metric: LWP (g/m2)
    # Metric: cloud fraction (%)     
    # Metric: max w variance (m2/s2) 
    # Metric: preciptation rate (mm/day)
    plots = ['LWP (g/m2)', 
             'cloud fraction (%)',
             'max w variance (m2/s2)',
             'preciptation rate (mm/day)'
    ] 

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
        
        ok = 0
        fail = 0

        # parse the control file
        control = parse_it(fns[f]['control'])
        experiment = parse_it(fns[f]['experiment'])
        # compare this against the control
        for v in control['stat'].keys():
            if control['stat'][v] != experiment['stat'][v]:
                print("\nDIFFERENCE IN VARIABLE "+v)
                print(control['stat'][v])
                print(experiment['stat'][v])
                fail+=1
            else:
                print("\nNO DIFFERENCE IN VARIABLE "+v)
                ok+=1
        # Print a summary for this comparison
        print("============================================")
        print("Summary for "+fns[f]['control']+" compared to "+fns[f]['experiment'])
        print(str(ok)+" stat variables are ok.")
        print(str(fail)+" stat variables show a difference.")
        print("\n\n")
        total_ok = total_ok+ok
        total_fail = total_fail+fail

    # Print a summary across all comparisons
    print("============================================")
    print("Summary for all comparisons")
    print(str(total_ok)+" stat variables are ok.")
    print(str(total_fail)+" stat variables show a difference.") 
    print("\n\n")

        # what are the log files to plot

        # create a dictionary that holds parsed values for each of the log files in the list
        # this list will have the plot values
        # we also need a list to compare the stat values and performance numbers

# grep for "stat::"

# DEBUG
#    for p in values.keys():
#        print ('\n')
#        print (p)
#        for fn in values[p].keys():
#            print('--------------------')
#            print(fn + "  " + fns[fn])
#            print(values[p][fn])

        # create plots
#        fig, ((pl1, pl2), (pl3,pl4)) = plt.subplots(2, 2, figsize=(12, 10))
#        plts = [pl1, pl2, pl3, pl4]


#  Need to find a better way to collese all of the information within one location!!!!!!!

#    def plot(_plt, i):
#        colors = []
#        for fn in sorted(fns.keys()):
#            if 'auto' in fns[fn]:
#                colors.append(_plt.plot(values[plots[i]][fn].keys(), values[plots[i]][fn].values())[0].get_color())
#            else:
#                colors.append(_plt.plot(values[plots[i]][fn].keys(), values[plots[i]][fn].values(), color=fns[fn])[0].get_color())
#        _plt.set_xlabel('time (min)')
#        _plt.set_ylabel(plots[i])
#        _plt.grid(linestyle='--')
#        return colors
#
#    for i in range(0, len(plts)):
#        colors = plot(plts[i], i)
#
#    lines = []
#    for c in colors:
#        lines.append(mlines.Line2D([], [], color=c))
#
#    fig.legend(handles=lines, labels=sorted(fns.keys()), loc = "lower center")
#    plt.subplots_adjust(bottom=0.25)
#
#    plt.show()

if __name__ == '__main__':
    read_logs("files.json")


