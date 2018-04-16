import fenics as fc
from scipy.interpolate import interp1d
import numpy as np
from scipy import sqrt, linspace
from ..math_functions import *
import sys

'''
Function: dataToHDF5
Argument list: fileName,distanceData, thicknessPathData, bedPathData, surfacePathData, smbPathData, velocityPathData, 
resolution(ideal resolution is 1000 for our dataset)
Purpose: Write our data that is pre determined to an HDF5 File
Return types, values:
Dependencies: interp1d from scipy, fenics package
Creator: James Stauder
Date created:2/23/18
Last edited: 2/23/18
'''


def dataToHDF5(fileName, distanceData, thicknessPathData, bedPathData, surfacePathData, smbPathData, velocityPathData,
               t2mPathData, widthData,xData, yData, resolution=1000):
    # Create interps for each of our variables

    thickness1dInterpAvg = interp1d(distanceData, thicknessPathData[1])
    bed1dInterpAvg = interp1d(distanceData, bedPathData[1])
    surface1dInterpAvg = interp1d(distanceData, surfacePathData[1])
    smb1dInterpAvg = interp1d(distanceData, smbPathData[1])
    velocity1dInterpAvg = interp1d(distanceData, velocityPathData[1])
    t2m1dInterpAvg = interp1d(distanceData, t2mPathData[1])

    thickness1dInterp = interp1d(distanceData, thicknessPathData[0])
    bed1dInterp = interp1d(distanceData, bedPathData[0])
    surface1dInterp = interp1d(distanceData, surfacePathData[0])
    smb1dInterp = interp1d(distanceData, smbPathData[0])
    velocity1dInterp = interp1d(distanceData, velocityPathData[0])
    t2m1dInterp = interp1d(distanceData, t2mPathData[0])

    width1dInterp = interp1d(distanceData, widthData)
    x1dInterp = interp1d(distanceData, xData)
    y1dInterp = interp1d(distanceData, yData)

    numberOfPoints = int(np.floor(distanceData[-1] / float(resolution)))

    x = np.arange(0, (numberOfPoints + 1) * resolution, resolution)

    mesh = fc.IntervalMesh(numberOfPoints, 0, resolution * numberOfPoints)

    thicknessModelData = thickness1dInterp(x)
    bedModelData = bed1dInterp(x)
    surfaceModelData = surface1dInterp(x)
    smbModelData = smb1dInterp(x)
    velocityModelData = velocity1dInterp(x)
    t2mModelData = t2m1dInterp(x)
    widthModelData = width1dInterp(x)
    xModelData = x1dInterp(x)
    yModelData = y1dInterp(x)

    thicknessModelDataAvg = thickness1dInterpAvg(x)
    bedModelDataAvg = bed1dInterpAvg(x)
    surfaceModelDataAvg = surface1dInterpAvg(x)
    smbModelDataAvg = smb1dInterpAvg(x)
    velocityModelDataAvg = velocity1dInterpAvg(x)
    t2mModelDataAvg = t2m1dInterpAvg(x)

    H = surfaceModelData - bedModelData
    HAvg = surfaceModelDataAvg - bedModelDataAvg

    surfaceModelData[H <= thklim] = bedModelData[H <= thklim]
    surfaceModelDataAvg[HAvg <= thklim] = bedModelDataAvg[HAvg <= thklim]

    fileName = '.data/' + fileName

    hfile = fc.HDF5File(mesh.mpi_comm(), '.data/latestProfile.h5', "w")
    profileFile = fc.HDF5File(mesh.mpi_comm(), str(fileName), "w")
    V = fc.FunctionSpace(mesh, "CG", 1)

    functThickness = fc.Function(V, name="Thickness")
    functBed = fc.Function(V, name="Bed")
    functSurface = fc.Function(V, name="Surface")
    functSMB = fc.Function(V, name="SMB")
    functVelocity = fc.Function(V, name="Velocity")
    functT2m = fc.Function(V, name="t2m")
    functWidth = fc.Function(V, name="width")
    functXValues = fc.Function(V, name='x')
    functYValues = fc.Function(V, name='y')

    functThicknessAvg = fc.Function(V, name="ThicknessAvg")
    functBedAvg = fc.Function(V, name="BedAvg")
    functSurfaceAvg = fc.Function(V, name="SurfaceAvg")
    functSMBAvg = fc.Function(V, name="SMBAvg")
    functVelocityAvg = fc.Function(V, name="VelocityAvg")
    functT2mAvg = fc.Function(V, name="t2mAvg")

    functThickness.vector()[:] = thicknessModelData
    functBed.vector()[:] = bedModelData
    functSurface.vector()[:] = surfaceModelData
    functSMB.vector()[:] = smbModelData
    functVelocity.vector()[:] = velocityModelData
    functT2m.vector()[:] = t2mModelData
    functWidth.vector()[:] = widthModelData
    functXValues.vector()[:] = xModelData
    functYValues.vector()[:] = yModelData

    functThicknessAvg.vector()[:] = thicknessModelDataAvg
    functBedAvg.vector()[:] = bedModelDataAvg
    functSurfaceAvg.vector()[:] = surfaceModelDataAvg
    functSMBAvg.vector()[:] = smbModelDataAvg
    functVelocityAvg.vector()[:] = velocityModelDataAvg
    functT2mAvg.vector()[:] = t2mModelDataAvg

    hfile.write(functThickness.vector(), "/thickness")
    hfile.write(functBed.vector(), "/bed")
    hfile.write(functSurface.vector(), "/surface")
    hfile.write(functSMB.vector(), "/smb")
    hfile.write(functVelocity.vector(), "/velocity")
    hfile.write(functT2m.vector(), "/t2m")

    hfile.write(functThicknessAvg.vector(), "/thicknessAvg")
    hfile.write(functBedAvg.vector(), "/bedAvg")
    hfile.write(functSurfaceAvg.vector(), "/surfaceAvg")
    hfile.write(functSMBAvg.vector(), "/smbAvg")
    hfile.write(functVelocityAvg.vector(), "/velocityAvg")
    hfile.write(functT2mAvg.vector(), "/t2mAvg")
    hfile.write(functWidth.vector(), "/width")
    hfile.write(functYValues.vector(), "/y")
    hfile.write(functXValues.vector(), "/x")
    hfile.write(mesh, "/mesh")

    profileFile.write(functThickness.vector(), "/thickness")
    profileFile.write(functBed.vector(), "/bed")
    profileFile.write(functSurface.vector(), "/surface")
    profileFile.write(functSMB.vector(), "/smb")
    profileFile.write(functVelocity.vector(), "/velocity")
    profileFile.write(functT2m.vector(), "/t2m")
    profileFile.write(functWidth.vector(), "/width")
    profileFile.write(functYValues.vector(), "/y")
    profileFile.write(functXValues.vector(), "/x")
    profileFile.write(mesh, "/mesh")

    profileFile.write(functThicknessAvg.vector(), "/thicknessAvg")
    profileFile.write(functBedAvg.vector(), "/bedAvg")
    profileFile.write(functSurfaceAvg.vector(), "/surfaceAvg")
    profileFile.write(functSMBAvg.vector(), "/smbAvg")
    profileFile.write(functVelocityAvg.vector(), "/velocityAvg")
    profileFile.write(functT2mAvg.vector(), "/t2mAvg")
    hfile.close()
    profileFile.close()


def interpolateFlowlineData(datasetDictionary, flowlines, midFlowline, flowlineDistance, dr, fileName):

    distanceBetweenPoints = sqrt(
        (midFlowline[1][0] - midFlowline[0][0]) ** 2 + (midFlowline[1][1] - midFlowline[0][1]) ** 2)
    distanceData = linspace(0, flowlineDistance, flowlineDistance / distanceBetweenPoints)

    #For each value in the dictionary create pathData list. Index 0 is the mid flowline and index 1 is the average
    for x in datasetDictionary:
        datasetDictionary[x].pathData = []

        # midFlowline path data
        pathData = []
        for y in midFlowline:
            pathData.append(datasetDictionary[x].getInterpolatedValue(y[0], y[1])[0][0])
        datasetDictionary[x].pathData.append(np.array(pathData))

        #average path data
        averagePathData = []
        for y in range(len(flowlines[0])):
            total = 0
            for z in range(len(flowlines)):
                total = total + datasetDictionary[x].getInterpolatedValue(flowlines[z][y][0], flowlines[z][y][1])[0][0]
            averagePathData.append(total/len(flowlines))
        datasetDictionary[x].pathData.append(np.array(averagePathData))

    #width data
    widthData = []
    for i in range(0, len(flowlines[2])):

        Points = [[flowlines[0][i][0], flowlines[0][i][1]],
                      [flowlines[1][i][0], flowlines[1][i][1]]]
        width = sqrt((Points[0][0] - Points[1][0])**2 + (Points[0][1] - Points[1][1])**2)
        widthData.append(width)
    widthData = np.array(widthData)

    xData = []
    yData = []
    for i in range(len(midFlowline)):
        xData.append(midFlowline[i][0])
        yData.append(midFlowline[i][1])

    # millimeters -> meters then water-equivalent to ice-equivalent
    datasetDictionary['smb'].pathData[0] = datasetDictionary['smb'].pathData[0] * (1.0 / 1000.0) * (916.7 / 1000.0)
    datasetDictionary['smb'].pathData[1] = datasetDictionary['smb'].pathData[1] * (1.0 / 1000.0) * (916.7 / 1000.0)

    dataToHDF5(fileName,
               distanceData,
               datasetDictionary['thickness'].pathData,
               datasetDictionary['bed'].pathData,
               datasetDictionary['surface'].pathData,
               datasetDictionary['smb'].pathData,
               datasetDictionary['velocity'].pathData,
               datasetDictionary['t2m'].pathData,
               widthData,
               xData,
               yData,
               resolution=dr)


