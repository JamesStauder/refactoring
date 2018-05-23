
import sys
import os
import glob
import json
from dolfin import project
import time

from helperFiles.classes.BlackBox import *


def main(argv):
    t0 = time.time()
    myFile = argv[1]
    directory = myFile
    os.chdir(directory)
    files = [file for file in glob.glob("*.h5")]
    charts = [True, False]
    sizes = [20, 50, 100]
    numYears = 500
    timeStep = 1

    for i in files:
        for j in sizes:
            jsonName = i[:-3] + '_' + str(j) + '.json'
            data = {}
            Max = -9999
            counter = 1
            for k in charts:
                chartKey = 'chart' + str(counter)
                counter = counter+1
                data[chartKey] = []

                tempBox = IceCube(i, numYears, timeStep, average=k)

                bedrock = project(tempBox.strs.B).compute_vertex_values()
                bedrock = list(bedrock)
                data['domain'] = len(list(bedrock))-1

                bedrock = bedrock[0:-1:len(bedrock)/j]
                data['bedrock'] = bedrock

                height = project(tempBox.strs.H0+tempBox.strs.B).compute_vertex_values()
                h0 = list(height)
                h0 = h0[0:-1:len(bedrock)/j]

                data[chartKey].append(h0)

                for x in h0:
                    if x > Max:
                        Max = x

                for _ in range(0, numYears):
                    BB, HH, TD, TB, TX, TY, TZ, us, ub = tempBox.runNextStep()
                    dataToAppend = list(BB+HH)
                    dataToAppend = dataToAppend[0:-1:(len(dataToAppend)/j)]
                    data[chartKey].append(dataToAppend)



            data['Max'] = Max


            for x in range(len(data['chart2'])):
                for z in range(len(data['chart2'][x])):
                    data['chart2'][x][z] = "{:4.1f}".format(data['chart2'][x][z])
                    data['chart2'][x][z] = float(data['chart2'][x][z])
            for x in range(len(data['chart1'])):
                for z in range(len(data['chart1'][x])):
                    data['chart1'][x][z] = "{:4.1f}".format(data['chart1'][x][z])
                    data['chart1'][x][z] = float(data['chart1'][x][z])
            for x in range(len(data['bedrock'])):
                data['bedrock'][x] = "{:4.1f}".format(data['bedrock'][x])
                data['bedrock'][x] = float(data['bedrock'][x])
            data['Max'] = "{:4.1f}".format(data['Max'])
            data['Max'] = float(data['Max'])
            with open(jsonName, 'w') as outfile:
                json.dump(data, outfile)


    print time.time() - t0

if __name__ == '__main__':
    main(sys.argv)
