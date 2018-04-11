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
               t2mPathData, widthData, resolution=1000):
    # Create interps for each of our variables
    thickness1dInterpAvg = interp1d(distanceData, thicknessPathData[0])
    bed1dInterpAvg = interp1d(distanceData, bedPathData[0])
    surface1dInterpAvg = interp1d(distanceData, surfacePathData[0])
    smb1dInterpAvg = interp1d(distanceData, smbPathData[0])
    velocity1dInterpAvg = interp1d(distanceData, velocityPathData[0])
    t2m1dInterpAvg = interp1d(distanceData, t2mPathData[0])

    thickness1dInterp = interp1d(distanceData, thicknessPathData[1])
    bed1dInterp = interp1d(distanceData, bedPathData[1])
    surface1dInterp = interp1d(distanceData, surfacePathData[1])
    smb1dInterp = interp1d(distanceData, smbPathData[1])
    velocity1dInterp = interp1d(distanceData, velocityPathData[1])
    t2m1dInterp = interp1d(distanceData, t2mPathData[1])

    width1dInterp = interp1d(distanceData, widthData)

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
    hfile.write(mesh, "/mesh")

    profileFile.write(functThickness.vector(), "/thickness")
    profileFile.write(functBed.vector(), "/bed")
    profileFile.write(functSurface.vector(), "/surface")
    profileFile.write(functSMB.vector(), "/smb")
    profileFile.write(functVelocity.vector(), "/velocity")
    profileFile.write(functT2m.vector(), "/t2m")
    profileFile.write(functWidth.vector(), "/width")
    profileFile.write(mesh, "/mesh")

    profileFile.write(functThicknessAvg.vector(), "/thicknessAvg")
    profileFile.write(functBedAvg.vector(), "/bedAvg")
    profileFile.write(functSurfaceAvg.vector(), "/surfaceAvg")
    profileFile.write(functSMBAvg.vector(), "/smbAvg")
    profileFile.write(functVelocityAvg.vector(), "/velocityAvg")
    profileFile.write(functT2mAvg.vector(), "/t2mAvg")
    hfile.close()
    profileFile.close()


def interpolateFlowlineData(datasetDictionary, flowlines, flowlineDistance, dr, fileName):
    distanceBetweenPoints = sqrt(
        (flowlines[2][1][0] - flowlines[2][0][0]) ** 2 + (flowlines[2][1][1] - flowlines[2][0][1]) ** 2)
    distanceData = linspace(0, flowlineDistance, flowlineDistance / distanceBetweenPoints)

    for x in datasetDictionary:
        pathData = []
        for i in flowlines[2]:
            pathData.append(datasetDictionary[x].getInterpolatedValue(i[0], i[1])[0][0])
        datasetDictionary[x].pathData.append(np.array(pathData))

        '''
        print x
        print datasetDictionary[x].pathData
        print ""
        '''

    widthData = []
    for i in range(0, len(flowlines[2])):

        Points = [[flowlines[0][i][0], flowlines[0][i][1]],
                      [flowlines[1][i][0], flowlines[1][i][1]]]
        width = sqrt((Points[0][0] - Points[1][0])**2 + (Points[0][1] - Points[1][1])**2)
        widthData.append(width)

    widthData = np.array(widthData)

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
               resolution=dr)


def interpolateFlowlineDataAverage(datasetDictionary, flowlines, flowlineDistance, dr, fileName):
    for x in datasetDictionary:
        pathData = []
        datasetDictionary[x].pathData = []
        for y in range(0,len(flowlines[0])):
            total = 0
            Points = [[flowlines[0][y][0], flowlines[0][y][1]],[flowlines[1][y][0], flowlines[1][y][1]]]
            width = sqrt((Points[0][0] - Points[1][0])**2 + (Points[0][1] - Points[1][1])**2)
            numPoints = int(width/100)
            dx = (flowlines[1][y][0] - flowlines[0][y][0])/numPoints
            dy = (flowlines[1][y][1] - flowlines[0][y][1])/numPoints
            currX = flowlines[0][y][0]
            currY = flowlines[0][y][1]
            for z in range(0, numPoints):
                total = total + datasetDictionary[x].getInterpolatedValue(currX, currY)[0][0]
                currX = currX + dx
                currY = currY + dy
            pathData.append(total/numPoints)
        datasetDictionary[x].pathData.append(np.array(pathData))
