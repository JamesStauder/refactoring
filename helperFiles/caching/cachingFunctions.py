import fenics as fc
from scipy.interpolate import interp1d
import numpy as np
from scipy import sqrt, linspace
from ..math_functions import *

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
    thickness1dInterp = interp1d(distanceData, thicknessPathData)
    bed1dInterp = interp1d(distanceData, bedPathData)
    surface1dInterp = interp1d(distanceData, surfacePathData)
    smb1dInterp = interp1d(distanceData, smbPathData)
    velocity1dInterp = interp1d(distanceData, velocityPathData)
    t2m1dInterp = interp1d(distanceData, t2mPathData)
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

    H = surfaceModelData - bedModelData

    surfaceModelData[H <= thklim] = bedModelData[H <= thklim]

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

    functThickness.vector()[:] = thicknessModelData
    functBed.vector()[:] = bedModelData
    functSurface.vector()[:] = surfaceModelData
    functSMB.vector()[:] = smbModelData
    functVelocity.vector()[:] = velocityModelData
    functT2m.vector()[:] = t2mModelData
    functWidth.vector()[:] = widthModelData

    hfile.write(functThickness.vector(), "/thickness")
    hfile.write(functBed.vector(), "/bed")
    hfile.write(functSurface.vector(), "/surface")
    hfile.write(functSMB.vector(), "/smb")
    hfile.write(functVelocity.vector(), "/velocity")
    hfile.write(functT2m.vector(), "/t2m")
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
        datasetDictionary[x].pathData = np.array(pathData)

    widthData = []
    for i in range(0, len(flowlines[2])):

        projPoints = [dataToProj(flowlines[0][i][0], flowlines[0][i][1]),
                      dataToProj(flowlines[1][i][0], flowlines[1][i][1])]
        width = sqrt((projPoints[0][0] - projPoints[1][0])**2 + (projPoints[0][1] - projPoints[1][1])**2)
        widthData.append(width)

    widthData = np.array(widthData)
    # millimeters -> meters then water-equivalent to ice-equivalent
    datasetDictionary['smb'].pathData = datasetDictionary['smb'].pathData * (1.0 / 1000.0) * (916.7 / 1000.0)

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

