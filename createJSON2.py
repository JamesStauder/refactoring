
import sys
import os
import glob
import json
from dolfin import project
import time
import h5py
from pyproj import Proj

from helperFiles.classes.BlackBox import *

def main(argv):
    t0 = time.time()
    myFile = argv[1]
    os.chdir(myFile)
    files = [file for file in glob.glob("*.h5")]
    charts = [True, False]
    size = 100
    numYears = 500
    timeStep = 1


    
    for i in files:
        jsonModelName = i[:-3] + '_Model.json' 
        data = {}
        Max = -9999
        domain = 1
        
        counter = 1
        for j in charts:
            chartKey = 'Chart' + str(counter)
            counter = counter + 1
            data[chartKey] = []
            
            tempBox = IceCube(i, numYears, timeStep, average=j)

            bedrock = project(tempBox.strs.B).compute_vertex_values()
            domain = len(list(bedrock))-1

            bedrock = list(bedrock)
            bedrock = bedrock[0::len(bedrock)/size]
            bedrockKey = 'bedrock' + chartKey
            data[bedrockKey] = bedrock

            height = project(tempBox.strs.H0+tempBox.strs.B).compute_vertex_values()
            h0 = list(height)
            h0 = h0[0::len(h0)/size]

            data[chartKey].append(h0)

            Max = max(h0)


            for _ in range(0, numYears):
                BB, HH, TD, TB, TX, TY, TZ, us, ub = tempBox.runNextStep()
                dataToAppend = list(BB+HH)
                dataToAppend = dataToAppend[0::(len(dataToAppend)/size)]
                Max = max([max(dataToAppend),Max])
                data[chartKey].append(dataToAppend)

          #Create the model run json file      
        for x in range(len(data['Chart2'])):
            for z in range(len(data['Chart2'][x])):
                data['Chart2'][x][z] = "{:4.1f}".format(data['Chart2'][x][z])
                data['Chart2'][x][z] = float(data['Chart2'][x][z])
        for x in range(len(data['Chart1'])):
            for z in range(len(data['Chart1'][x])):
                data['Chart1'][x][z] = "{:4.1f}".format(data['Chart1'][x][z])
                data['Chart1'][x][z] = float(data['Chart1'][x][z])
        for x in range(len(data['bedrockChart1'])):
            data['bedrockChart1'][x] = "{:4.1f}".format(data['bedrockChart1'][x])
            data['bedrockChart1'][x] = float(data['bedrockChart1'][x])
        for x in range(len(data['bedrockChart2'])):
            data['bedrockChart2'][x] = "{:4.1f}".format(data['bedrockChart2'][x])
            data['bedrockChart2'][x] = float(data['bedrockChart2'][x])
        with open(jsonModelName, 'w') as outfile: 
            json.dump(data, outfile)
            




        jsonShapeName = i[:-3] + '_Shape.json'
        data = {}
        data['ID'] = i[:-3]
        data['Max'] = Max
        data['Max'] = "{:4.1f}".format(data['Max'])
        data['Max'] = float(data['Max'])
        data['domain'] = domain


        f = h5py.File(i, 'r')
        midX = f['Mid_x'][:]
        midY = f['Mid_y'][:]
        shear1X = f['Shear_0_x'][:]
        shear2X = f['Shear_1_x'][:]
        shear1Y = f['Shear_0_y'][:]
        shear2Y = f['Shear_1_y'][:]


        coords1 = []
        coords2 = []
        midCoords = []
        for a in range(len(shear1X)):
            coords1.append([shear1X[a], shear1Y[a]])
            coords2.append([shear2X[a], shear2Y[a]])
            midCoords.append([midX[a], midY[a]])

        initProj = Proj(init = 'epsg:3413')


        for a in range(len(coords1)):
            lons, lat = initProj(coords1[a][0], coords1[a][1], inverse = True)
            coords1[a] = [lons, lat]

            lons, lat = initProj(coords2[a][0], coords2[a][1], inverse = True)
            coords2[a] = [lons, lat]

            lons, lat = initProj(midCoords[a][0], midCoords[a][1], inverse = True)
            midCoords[a] = [lons, lat]
            


        data['Shear1'] = coords1
        data['Shear2'] = coords2
        data['Midline'] = midCoords

        for x in range(len(data['Shear1'])):
            data['Shear1'][x][0] = "{:4.3f}".format(data['Shear1'][x][0])
            data['Shear1'][x][0] = float(data['Shear1'][x][0])
            data['Shear1'][x][1] = "{:4.3f}".format(data['Shear1'][x][1])
            data['Shear1'][x][1] = float(data['Shear1'][x][1])

        for x in range(len(data['Shear2'])):
            data['Shear2'][x][0] = "{:4.3f}".format(data['Shear2'][x][0])
            data['Shear2'][x][0] = float(data['Shear2'][x][0])
            data['Shear2'][x][1] = "{:4.3f}".format(data['Shear2'][x][1])
            data['Shear2'][x][1] = float(data['Shear2'][x][1])
        for x in range(len(data['Midline'])):
            data['Midline'][x][0] = "{:4.3f}".format(data['Midline'][x][0])
            data['Midline'][x][0] = float(data['Midline'][x][0])
            data['Midline'][x][1] = "{:4.3f}".format(data['Midline'][x][1])
            data['Midline'][x][1] = float(data['Midline'][x][1])


        with open(jsonShapeName, 'w') as outfile:
            json.dump(data, outfile)








    print time.time() - t0

if __name__ == '__main__':
    main(sys.argv)
