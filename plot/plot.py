import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import json
import numpy as np
from collections import OrderedDict


def plot_it(json_file):
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
    print('Using these log files ....')
    for f in sorted(fns.keys()):
        print(f)
    print("\n")


    # setup the dict that will hold all of the values
    values = {}
    for p in plots:
        values[p] = OrderedDict()
        for fn in sorted(fns.keys()):
            values[p][fn]=OrderedDict()

    # parse out the values
    for fn in sorted(fns.keys()):
        with open(fn) as f:
            for l in f:
                if 'Metric' in l:
                    values[l.split('Metric:')[-1].strip().split('=')[0].strip()][fn][ts] = float(l.split('=')[-1])
                    #print(str(ts)+" "+str(float(l.split('=')[-1])))
                if 'nwritet =' in l:
                    ts = int(l.split('nwritet =')[-1].strip())

# DEBUG
#    for p in values.keys():
#        print ('\n')
#        print (p)
#        for fn in values[p].keys():
#            print('--------------------')
#            print(fn + "  " + fns[fn])
#            print(values[p][fn])

    # create plots
    fig, ((pl1, pl2), (pl3,pl4)) = plt.subplots(2, 2, figsize=(12, 10))
    plts = [pl1, pl2, pl3, pl4]


    def plot(_plt, i):
        colors = []
        for fn in sorted(fns.keys()):
            if 'auto' in fns[fn]:
                colors.append(_plt.plot(values[plots[i]][fn].keys(), values[plots[i]][fn].values())[0].get_color())
            else:
                colors.append(_plt.plot(values[plots[i]][fn].keys(), values[plots[i]][fn].values(), color=fns[fn])[0].get_color())
        _plt.set_xlabel('time (min)')
        _plt.set_ylabel(plots[i])
        _plt.grid(linestyle='--')
        return colors

    for i in range(0, len(plts)):
        colors = plot(plts[i], i)

    lines = []
    for c in colors:
        lines.append(mlines.Line2D([], [], color=c))

    fig.legend(handles=lines, labels=sorted(fns.keys()), loc = "lower center")
    plt.subplots_adjust(bottom=0.25)

    plt.show()

if __name__ == '__main__':
    plot_it("files.json")
