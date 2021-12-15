import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import json
import numpy as np
from collections import OrderedDict

def parse_it(log_file):

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
               info['metrics'][line.split('Metric:')[-1].strip().split('=')[0].strip()].append(float(line.split()[-1]))               
            # performance and total time collection
            elif in_timing_section and ':' in line and len(line.split())==4:
                split = line.split()
                info['performance'][split[0].strip()] = split[-1].strip().replace("%","")
            elif 'Total time:' in line:
                 info['total_time'] = line.split()[-1].strip()
                 in_timing_section = True

    return info


def performance_plot(Ctimings, Ctitle, Etimings, Etitle):

    # combine low values
    low = 2.0
    # control 
    Cnew_timings = {'other':0}
    for k in Ctimings.keys():
        if float(Ctimings[k]) >= low:
            Cnew_timings[k] = float(Ctimings[k])
        else:
            Cnew_timings['other'] += float(Ctimings[k])
    #experiment
    Enew_timings = {'other':0}
    for k in Etimings.keys():
        if float(Etimings[k]) >= low:
            Enew_timings[k] = float(Etimings[k])
        else:
            Enew_timings['other'] += float(Etimings[k])

    fig1, ax1 = plt.subplots(2,figsize=(15,15))
    ax1[0].pie(Cnew_timings.values(), labels=Cnew_timings.keys(), autopct='%1.1f%%')
    ax1[1].pie(Enew_timings.values(), labels=Enew_timings.keys(), autopct='%1.1f%%')
    ax1[0].set_title(Ctitle,fontsize=10)
    ax1[1].set_title(Etitle,fontsize=10)
    plt.show()


def line_info(_plt, Cvalues, Evalues, label):
        colors = []
        sub = []
        for i in range(len(Cvalues)):
            sub.append(Cvalues[i]-Evalues[i])
        colors.append(_plt.plot(sub))
        _plt.set_xlabel('time (min)')
        _plt.set_ylabel(label)
        _plt.grid(linestyle='--')
        return colors


def metric_plots(Cvalues, Evalues):

    fig, ((pl1, pl2), (pl3,pl4)) = plt.subplots(2, 2, figsize=(12, 10))
    plts = [pl1, pl2, pl3, pl4]

    for i,label in enumerate(Cvalues.keys()):
        colors = line_info(plts[i], Cvalues[label], Evalues[label], label)

    plt.subplots_adjust(bottom=0.25)

    plt.show()


def read_logs(json_file):

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
        for v in control['stats'].keys():
            if control['stats'][v] != experiment['stats'][v]:
                print("\nDIFFERENCE IN VARIABLE "+v)
                print(control['stats'][v])
                print(experiment['stats'][v])
                fail+=1
            else:
                print("\nNO DIFFERENCE IN VARIABLE "+v)
                ok+=1

        # print and plot performance
        print("control(%) vs. experiment(%)")
        for v in control['performance']:
            print(v+": "+control['performance'][v]+"  "+experiment['performance'][v])
        performance_plot(control['performance'],fns[f]['control']+"\n Total Time: "+control['total_time']+" (seconds)",
                         experiment['performance'],fns[f]['experiment']+"\n Total Time: "+experiment['total_time']+" (seconds)")

        # create metric plots
        metric_plots(control['metrics'], experiment['metrics'])

        # Print the answer summary for this comparison
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


