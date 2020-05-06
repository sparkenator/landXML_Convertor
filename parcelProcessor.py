'''
Author: S Parkes
Version: 1.0
Date: 11/02/2020

Collects parcel info and adds them to class instances to create mxl file
'''

import numpy as np
from scipy.stats import mode
import genericFunctions as funcs

def main(parcelList, pointList, lineList, curveList, **kwargs):
    '''
    function collects parcel information from land xml file.
    Class instance created to store parcel information and points are added to pointList, lines
     added to lineList, and curves to curveList instances
    :param parcelList: parcel instance to store parcel info - mainly for text labels
    :param pointList: points instance
    :param lineList: lines instance
    :param curveList: curves instance
    :param kwargs: dictionary with function arguments - needs
    :return: pointList, curveList, lineList, parcelList
    '''

    parcelList, pointList, lineList, curveList = collectParcelData(parcelList, pointList, lineList, curveList,
                                                                   "landParcels", **kwargs)

    parcelList, pointList, lineList, curveList = collectParcelData(parcelList, pointList, lineList, curveList,
                                                                   "Easements", **kwargs)

    parcelList, pointList, lineList, curveList = collectParcelData(parcelList, pointList, lineList, curveList,
                                                                   "Road", **kwargs)

    return parcelList, pointList, lineList, curveList

def collectParcelData(parcelList, pointList, lineList, curveList, ParcelType, **kwargs):
    '''
    collects the parcel information and data for ParcelType (Easements, new lots, and Roads)
    :param parcelList:
    :param pointList:
    :param Linelist:
    :param curveList:
    :param ParcelType:
    :param kwargs:
    :return:
    '''

    #loop through parcels and get parcel info and linework - add to respective instances
    for parcel in kwargs["lxmlObj"].find(kwargs["lxmlNamespace"] + "Parcels").getchildren():

        if ParcelType == "landParcels":
            parcelList, pointList, lineList, curveList = landParcels(parcel, parcelList, pointList,
                                                                     lineList, curveList, **kwargs)

        elif ParcelType == "Easements":
            parcelList, pointList, lineList, curveList = easementParcels(parcel, parcelList, pointList,
                                                                         lineList, curveList, **kwargs)

        elif ParcelType == "Road": #Road
            parcelList, pointList, lineList, curveList = roadParcels(parcel, parcelList, pointList,
                                                                         lineList, curveList, **kwargs)


    return parcelList, pointList, lineList, curveList

def landParcels(parcel, parcelList, pointList, lineList, curveList, **kwargs):
    '''
    processes land parcel - parcel element
    :param parcel:
    :param parcelList:
    :param pointList:
    :param Linelist:
    :param curveList:
    :param kwargs:
    :return:
    '''

    parcelClass = parcel.get("class")
    parcelState = parcel.get("state")
    # see if parcel is in new sub divisions
    if parcelClass == "Lot" and parcelState == "proposed":  # land parcel
        # add parcelInfo to parcelList
        landType = "Parcel"
        parcelList = collectParcelInfo(parcel, landType, parcelList, **kwargs)
        parcelList.landType.append(landType)

        # add coordinate and linework inforation to class instances
        #kwargs["layerID"] = mxlCollect.getLayerFromMxlTemplate("BOUNDARY", **kwargs)
        kwargs["layerName"] = "BOUNDARY"
        kwargs['code'] = ""
        #kwargs["colourCode"] = mxlCollect.getColourCodeFromMxlTemplate("BOUNDARY", **kwargs)
        pointList, lineList, curveList = collectParcelLineWork(parcel, pointList, lineList, curveList, **kwargs)

    return parcelList, pointList, lineList, curveList


def easementParcels(parcel, parcelList, pointList, lineList, curveList, **kwargs):
    '''
    processes easement parcel - parcel element
    :param parcel:
    :param parcelList:
    :param pointList:
    :param Linelist:
    :param curveList:
    :param kwargs:
    :return:
    '''

    parcelNum = parcel.get("name")
    # see if easement parcel
    if "E" in parcelNum:
        # add coordinate and linework inforation to class instances
        #kwargs["layerID"] = mxlCollect.getLayerFromMxlTemplate("EASEMENT", **kwargs)
        kwargs["layerName"] = "EASEMENT"
        kwargs['code'] = ""
        #kwargs["colourCode"] = mxlCollect.getColourCodeFromMxlTemplate("EASEMENT", **kwargs)
        pointList, lineList, curveList = collectParcelLineWork(parcel, pointList, lineList, curveList, **kwargs)

    return parcelList, pointList, lineList, curveList

def roadParcels(parcel, parcelList, pointList, lineList, curveList, **kwargs):
    '''
    processes easement parcel - parcel element
    :param parcel:
    :param parcelList:
    :param pointList:
    :param Linelist:
    :param curveList:
    :param kwargs:
    :return:
    '''


    parcelNum = parcel.get("name")
    # see if easement parcel
    if "R" in parcelNum:
        # add parcelInfo to parcelList
        landType = "Road"
        parcelList = collectParcelInfo(parcel, landType, parcelList, **kwargs)
        parcelList.landType.append(landType)
        # add coordinate and linework inforation to class instances
        #kwargs["layerID"] = mxlCollect.getLayerFromMxlTemplate("BOUNDARY", **kwargs)
        kwargs["layerName"] = "BOUNDARY"
        kwargs['code'] = ""
        #kwargs["colourCode"] = mxlCollect.getColourCodeFromMxlTemplate("BOUNDARY", **kwargs)

        pointList, lineList, curveList = collectParcelLineWork(parcel, pointList, lineList, curveList, **kwargs)

    return parcelList, pointList, lineList, curveList

def collectParcelInfo(parcel, landType, parcelList, **kwargs):
    '''
    Collects parcel Info from parcel attributes and gets pntRef for centre of parcel
    :param parcelNum: parcelName (for roads parcelNum is given road name)
    :param parcelArea: area of parcel - noneType for roads
    :param landType: road or parcel
    :return: parcelList
    '''

    for parcelInfo in parcel.getchildren():
        if (kwargs["lxmlNamespace"] + "Center") == parcelInfo.tag:  # parcel info

            parcelList.centerRef.append(parcelInfo.get('pntRef'))
            East, North = getCoords(parcelInfo.get('pntRef'), **kwargs)
            parcelList.centerRefE.append(East)
            parcelList.centerRefN.append(North)

            if landType == "Parcel":
                parcelList.Name.append(parcel.get("name"))
                parcelList.AreaRotation.append(parcel.get("area"))
            else:
                parcelList.AreaRotation.append(roadOrientation(parcel, **kwargs))
                parcelList.Name.append(parcel.get("desc"))

    return parcelList


def collectParcelLineWork(parcel, pointList, lineList, curveList, **kwargs):
    '''
    retrieves parcel linework and adds to class instances
    :param parcel: parcel element to query
    :param pointList: see above in main
    :param lineList:  see above in main
    :param curveList:  see above in main
    :return: pointList, lineList, curveList
    '''


    for parcelInfo in parcel.getchildren():
        if (kwargs["lxmlNamespace"] + "CoordGeom") == parcelInfo.tag:
            pointList, lineList, curveList = getLinework(parcelInfo, pointList, lineList, curveList, \
                                                         **kwargs)

    return pointList, lineList, curveList

def getLinework(parcelInfo, pointList, lineList, curveList, **kwargs):
    '''
    Adds line work and points to instances
    :param parcelInfo: xml element with linework
    :return: pointList, lineList, curveList
    '''

    #loop through linework elements
    for child in parcelInfo.getchildren():
        startRef = child.find(kwargs["lxmlNamespace"] + "Start").values()[0]
        endRef = child.find(kwargs["lxmlNamespace"] + "End").values()[0]
        if type(startRef) != str:
            print("startRef")
            break
        if type(endRef) != str:
            print("endRef")
            break
        if child.tag == (kwargs["lxmlNamespace"] + "Curve"):
            centRef = child.find(kwargs["lxmlNamespace"] + "Center").values()[0]
            radius = child.get("radius")
            curveList, pointList = curveWork(curveList, pointList, child, startRef, endRef,
                                             centRef, radius, **kwargs)

        elif child.tag == (kwargs["lxmlNamespace"] + "Line"):
            lineList, pointList = lineWork(lineList, pointList, startRef, endRef, **kwargs)

    return pointList, lineList, curveList


def curveWork(curveList, pointList, child, startRef, endRef, centRef, radius, **kwargs):
    '''
    Adds info for curve to curveList instance
    :param curveList: instance
    :return: curveList
    '''

    #process curve and check already entered
    if not checkNewLine(curveList, startRef, endRef): #if line not already recorded

        #Add item attributes
        curveList.rotation.append(child.get('rot'))
        curveList.radius.append(child.get('radius'))
        #curveList.layerID.append(kwargs["layerID"])
        curveList.layerName.append(kwargs["layerName"])
        #curveList.colourCode.append(kwargs["colourCode"])
        #add curve elements - add start angle
        curveList.startRef.append(startRef)
        East, North = getCoords(startRef, **kwargs)
        curveList.startE.append(East)
        curveList.startN.append(North)
        #add point coordinates and references
        if startRef not in pointList.pntRef:
            pointList = addPoints(pointList, startRef, East, North, **kwargs)

        #end of curve - add angle
        curveList.endRef.append(endRef)
        East, North = getCoords(endRef, **kwargs)
        curveList.endE.append(East)
        curveList.endN.append(North)

        if endRef not in pointList.pntRef:
            pointList = addPoints(pointList, endRef, East, North, **kwargs)

        #centre reference
        curveList.centRef.append(centRef)
        East, North = getCoords(centRef, **kwargs)
        curveList.centE.append(East)
        curveList.centN.append(North)

        #calculate angles using arctan2 -> for use in dxf files
        startAngle, endAngle = calcCurveAngles(curveList)

        if child.get('rot') == 'ccw':
            # calculate angles for start and end of arc
            curveList.startAngle.append(startAngle)
            curveList.endAngle.append(endAngle)
        else:
            # calculate angles for start and end of arc
            curveList.startAngle.append(endAngle)
            curveList.endAngle.append(startAngle)

        '''
        #calculate the bulge for mxl file
        chord = np.sqrt((float(curveList.endE[-1]) - float(curveList.startE[-1]))**2 +\
                        (float(curveList.endN[-1]) - float(curveList.startN[-1]))**2)
        height = float(curveList.radius[-1]) - np.sqrt(float(curveList.radius[-1])**2 - (chord / 2)**2)
        Bulge = -(height / (chord / 2))
        if curveList.rotation[-1] == "ccw":
            Bulge = - Bulge

        curveList.bulge.append(Bulge)
        '''
    return curveList, pointList

def calcCurveAngles(curveList):
    '''
    using arctan2 calculates the angles of the start and end of curve.
    In DXF start and end angles are angle relative to the x-axis (180 > theta > -180)
    :param curveList:
    :return: startAngle, endAngle
    '''

    #start Angle
    startN = np.array(curveList.startN[-1]) - np.array(curveList.centN[-1])
    startE = np.array(curveList.startE[-1]) - np.array(curveList.centE[-1])
    startAngle = np.degrees(np.arctan2(startN, startE))
    #end Angle
    endN = np.array(curveList.endN[-1]) - np.array(curveList.centN[-1])
    endE = np.array(curveList.endE[-1]) - np.array(curveList.centE[-1])
    endAngle = np.degrees(np.arctan2(endN, endE))

    return startAngle, endAngle

def lineWork(lineList, pointList, startRef, endRef, **kwargs):
    '''
    Adds info for line to lineList instance
    :param curveList: instance
    :return: curveList
    '''

    #process curve and check already entered
    if not checkNewLine(lineList, startRef, endRef): #if line not already recorded

        #Add item attributes
        #lineList.layerID.append(kwargs["layerID"])
        lineList.layerName.append(kwargs["layerName"])
        #lineList.colourCode.append(kwargs["colourCode"])

        # add curve elements
        lineList.startRef.append(startRef)
        East, North = getCoords(startRef, **kwargs)
        lineList.startE.append(East)
        lineList.startN.append(North)
        # add point coordinates and references
        if startRef not in pointList.pntRef:
            pointList = addPoints(pointList, startRef, East, North, **kwargs)

        # end of curve
        lineList.endRef.append(endRef)
        East, North = getCoords(endRef, **kwargs)
        lineList.endE.append(East)
        lineList.endN.append(North)

        if endRef not in pointList.pntRef:
            pointList = addPoints(pointList, endRef, East, North, **kwargs)

    return lineList, pointList

def getCoords(pntRef, **kwargs):
    '''
    gets coordinates of pntRef
    :param pntRef: point reference in CG points of landXML file
    :return: East, North
    '''

    # get coordinates of SSM 'X'
    for child in kwargs["lxmlObj"].find(kwargs["lxmlNamespace"] + "CgPoints").getchildren():
        if child.get("name") == pntRef:
            East = float(child.text.split(' ')[1])
            North = float(child.text.split(' ')[0])

    return East, North

def addPoints(pointList, pointRef, East, North, **kwargs):
    '''
    Adds points and their coordinates and codes etc to pointList
    :param pointList:
    :return: pointList
    '''

    if not checkNewPoint(pointList, pointRef):
        pointList.pntRef.append(pointRef)
        pointList.pntE.append(East)
        pointList.pntN.append(North)
        #pointList.pntCodeID.append(kwargs["code"])
        pointList.pntCodeName.append(kwargs["code"])
        #pointList.layerID.append(kwargs["layerID"])
        pointList.layerName.append(kwargs["layerName"])
        #pointList.colourCode.append(kwargs["colourCode"])

    return pointList

def checkNewPoint(pointList, pntRef):
    '''
    Checks to see if point has not already been entered into pointList
    :param pointList:
    :param pntRef:
    :return:
    '''

    if pntRef in pointList.pntRef:
        return True
    else:
        return False

def checkNewLine(list, startRef, endRef):
    '''
    Checks to see if line already exists in line or curve list. As defined by start and end refs
    :param list:
    :param startRef:
    :param endRef:
    :return:
    '''


    #loop through starting points
    for i, startRefi in enumerate(list.startRef):
        endRefi = list.endRef[i]

        if startRef == startRefi and endRef == endRefi: #check same orientation
            return True
        elif endRef == startRefi and startRef == endRefi: #check reverese orientation
            return True


    return False


def roadOrientation(parcel, **kwargs):
    '''
    calculates road orientation from first road linework element
    :param parcel: parcel element from lxml
    :return: orientation
    '''

    #create list to store orientations of each line segment
    #calculate mode of all orientations for label and make sure <180
    #this is done because lots of segments aren't parrallel to road
    #use orientation as degrees.minutes (as small variations in seconds means mode doesn't work)
    orientation = []
    for child in parcel.getchildren():
        if (kwargs["lxmlNamespace"] + "CoordGeom") == child.tag:
            for elem in child.getchildren():
                if elem.tag == (kwargs["lxmlNamespace"] + "Line"):
                    startPntRef = elem.find(kwargs["lxmlNamespace"] + "Start").values()[0]
                    endPntRef = elem.find(kwargs["lxmlNamespace"] + "End").values()[0]
                    orientation.append(calcOrientation(startPntRef, endPntRef, **kwargs))
                    #print("Orientation: " + str(calcOrientation(startPntRef, endPntRef, **kwargs)))
    #orientation = calcOrientation(startPntRef, endPntRef, **kwargs)

    return mode(orientation)[0][0]

def calcSegLength(startPntRef, endPntRef, **kwargs):
    #get coordinates of start and end reference points
    CgPoints = kwargs["lxmlObj"].find(kwargs["lxmlNamespace"] + "CgPoints")
    for child in CgPoints.getchildren():
        if child.get("name") == startPntRef:
            startE = float(child.text.split(" ")[1])
            startN = float(child.text.split(" ")[0])
        elif child.get("name") == endPntRef:
            endE = float(child.text.split(" ")[1])
            endN = float(child.text.split(" ")[0])

    #calc changes in easting and northings
    deltaE = endE - startE
    deltaN = endN - startN

    return np.sqrt(deltaE**2+deltaN**2)

def calcOrientation(startPntRef, endPntRef, **kwargs):
    '''
    calcs azimuth between two reference points
    finds eastings and northings in lxml file
    :param startPntRef: Start Point
    :param endPntRef: End Point
    :param kwargs:
    :return: azimuth
    '''

    #get coordinates of start and end reference points
    CgPoints = kwargs["lxmlObj"].find(kwargs["lxmlNamespace"] + "CgPoints")
    for child in CgPoints.getchildren():
        if child.get("name") == startPntRef:
            startE = float(child.text.split(" ")[1])
            startN = float(child.text.split(" ")[0])
        elif child.get("name") == endPntRef:
            endE = float(child.text.split(" ")[1])
            endN = float(child.text.split(" ")[0])

    #calc changes in easting and northings
    deltaE = endE - startE
    deltaN = endN - startN
    angle = np.degrees(np.arctan(np.abs(deltaN)/np.abs(deltaE)))

    #azimuth
    if deltaE > 0 and deltaN > 0:
        azimuth = 90 - angle
        azimuth = getDMS(azimuth)
    elif deltaE > 0 and deltaN < 0:
        azimuth = 90 + angle
        azimuth = getDMS(azimuth)
    elif deltaE < 0 and deltaN < 0:
        azimuth = 270 - angle
        azimuth = getDMS(azimuth)
    elif deltaE < 0  and deltaN > 0:
        azimuth = 270 + angle
        azimuth = getDMS(azimuth)
    elif deltaE == 0 and deltaN > 0:
        azimuth = str(0.0000)
    elif deltaE == 0 and deltaN < 0:
        azimuth = str(180.0000)
    elif deltaE > 0 and deltaN == 0:
        azimuth = str(90.0000)
    else:
        azimuth = str(270.0000)

    #rotate for magnet - subtract 90 degrees
    azimuth = str(np.round((float(azimuth)-90),2))+"00"
    if float(azimuth) < 0:
        azimuth = str(np.round((float(azimuth) + 360), 2)) + "00"

    #make sure less than 180 degrees
    if float(azimuth) >= 180:
        azimuth = str(np.round((float(azimuth)-180),2))+"00"

    azimuth = "-"+azimuth

    return azimuth

def getDMS(azimuth):
    '''
    converts azimuth to degrees.minutes seconds as string type
    :param azimuth: decimal azimuth
    :return: azDMS
    '''

    #Calc degrees, minutes, seconds
    degrees = np.floor(azimuth)
    minutes = np.round((((azimuth - degrees) * 60)),0)
    #seconds = ((azimuth - degrees) * 60 - minutes) * 60

    #convert to string type
    degrees = str(degrees).split(".")[0]

    if minutes < 10:
        minutes = "0" + str(minutes).split(".")[0]
    else:
        minutes = str(minutes).split(".")[0]

    #seconds = str(seconds).split(".")[0]

    azDMS = str(degrees) + "." + str(minutes) + "00"# + str(seconds)

    return azDMS


