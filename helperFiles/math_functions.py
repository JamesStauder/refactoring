from constants import *

'''
colorToProj:  color -> projected
dataToProj:   data -> projected
colorCoord:   data, projected -> color
dataToColor:  data -> color
colorToData:  color -> data
dataCoord:    color, projected -> data
'''


def colorToProj(x, y):
    # returns x,y in the global projected coordinates
    # no way to check if in color or map coord
    if map['cmap_proj_y1'] <= y <= map['cmap_proj_y0']:
        if map['cmap_proj_x0'] <= x <= map['cmap_proj_x1']:
            return x, y
        else:
            print 'ERROR IN PROJ COORD'
            return -1
    else:
        return ((150*x) + float(map['cmap_proj_x0'])), ((-150*y) + float(map['cmap_proj_y0']))


def dataToProj(x, y):
    return dataToColor(colorToProj(x, y))


def colorCoord(x, y):
    # must assume data in data coord or proj coord
    # first return data to color
    # else return proj to map
    if map['y0'] <= y <= map['y1']:
        if map['x0'] <= x <= map['x1']:
            return dataToColor(x, y)
        else:
            print 'ERROR IN MAP COORD'
            return -1
    else:
        return ((-float(map['cmap_proj_x0']) + x)/150.0), (-(-float(map['cmap_proj_y0']) + y)/150.0)


def dataToColor(x, y):
    # turns colormap data point into data point
    return x*(float(map['cmap_x1'])/float(map['x1'])), y*(float(map['cmap_y1'])/float(map['y1']))


def colorToData(x, y):
    # turns colormap data point into data point
    return x*(float(map['x1'])/float(map['cmap_x1'])), y*(float(map['y1'])/float(map['cmap_y1']))


def dataCoord(x, y):
    # must assume data is in colormap or projected coord

    if map['cmap_y0'] <= y <= map['cmap_y1']:
        if map['cmap_x0'] <= x <= map['cmap_x1']:
            return colorToData(x, y)
    elif map['cmap_proj_y0'] <= y <= map['cmap_proj_y1']:
        if map['cmap_proj_x0'] <= x <= map['cmap_proj_x1']:
            return colorToData(colorCoord(x, y))
    else:
        print 'ERROR: dataCoord(x, y) error'
        return -1






