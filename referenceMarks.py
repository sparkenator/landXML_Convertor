'''
Author: S Parkes
Version: 1.0
Date: 12/02/2020

Retrieves reference marks coordinates and connections

'''

import parcelProcessor

def main(pointList, lineList, **kwargs):
    '''
    Calls landXML object to first collect names and coordinates from Monument and CgPoints elements
    The connections are then determined from the Survey element for linework
    :param pointList: list of points to be written to the MXL file
    :param lineList: list of lines to be written to the MXL file
    :param kwargs:
    :return:
    '''

    #get monument element
    monuments = kwargs["lxmlObj"].find(kwargs["lxmlNamespace"] + "Monuments")
    kwargs["layerName"] = "REFERENCE MARKS"
    RM_refPnts = []
    #loop through monuments and get point information
    for monument in monuments.getchildren():
        pointList.layerName.append(kwargs['layerName'])
        #set RM_type
        if monument.get("type") == None:
            RM_type = monument.get("state")
        else:
            RM_type = monument.get("type")

        #assign monument code
        if "DH&W" == RM_type:
            codeValue = "RMDHW"
            pointList.pntCodeName.append(codeValue)

        elif RM_type == "SSM" or RM_type == "PM": #get and assign RM numbers
            codeValue = RM_type + getRmNumber(monument, **kwargs)
            if RM_type == "SSM":
                description = "RM STATE SURVEY MARK"
            else:
                description = "RM PERMANENT MARK"

            pointList.pntCodeName.append(codeValue)
        else:
            codeValue = "RM" + RM_type
            if monument.get("desc") == "NOW GONE":
                codeValue = codeValue + " GONE"

            pointList.pntCodeName.append(codeValue)


        # get point Coordinates
        East, North = parcelProcessor.getCoords(monument.get('pntRef'), **kwargs)
        pointList.pntE.append(East)
        pointList.pntN.append(North)

        # CHange Ref number in pointList if it already exists for a BDY
        if monument.get('pntRef') in pointList.pntRef:
            pointList.pntRef.append(str(max([int(i) for i  in pointList.pntRef])+1))  # add point reference
        else:
            pointList.pntRef.append(monument.get('pntRef'))
            RM_refPnts.append(monument.get('pntRef'))

    lineList = createRM_lineWork(lineList, pointList, RM_refPnts, **kwargs)

    return pointList, lineList, kwargs["lxmlObj"]#, kwargs["mxlRoot"]


def getRmNumber(monument, **kwargs):
    '''
    Retrieves the SSM number from the CgPoints using pnt Ref number
    :param pntRef:
    :param kwargs:
    :return:
    '''

    CgPoints = kwargs["lxmlObj"].find(kwargs["lxmlNamespace"] + "CgPoints")
    for pnt in CgPoints.getchildren(): #loop through points
        if pnt.get("name") == monument.get('pntRef'): #see if point match pntRef
            if pnt.get("oID") == None:
                idNum = monument.get("desc")
            else:
                idNum = pnt.get("oID") #assign RM number
            break

    return idNum

def createRM_lineWork(lineList, pointList, RM_refPnts, **kwargs):
    '''
    Adds RM linework to lineList
    :param lineList:
    :param pointList:
    :param RM_refPnts:
    :param kwargs:
    :return:
    '''

    #load survey element of lxmlObj and retrieve Observation group
    survey = kwargs["lxmlObj"].find(kwargs["lxmlNamespace"] + "Survey")

    for Observations in survey.getchildren():
        if Observations.tag == (kwargs["lxmlNamespace"] + "ObservationGroup"):
            break
    #loop through RM marks and find connections and add to lineList
    for RM in RM_refPnts:
        # retrieve RM_refPnt id
        idSetup = getIdFromSurvey(RM, survey, **kwargs)
        #loop through observations to find RM as setupID
        for obs in Observations.getchildren():
            if obs.get("setupID") == idSetup  and\
                    obs.tag == (kwargs["lxmlNamespace"]+"ReducedObservation"):

                try:
                    connection = obs.get('targetSetupID')
                    connectionRefPnt = getPntRefFromSurvey(connection, survey, **kwargs)
                    # check connection point exists in pointList
                    if RM in pointList.pntRef and connectionRefPnt in pointList.pntRef:
                        #add linework
                        lineList, pointList = parcelProcessor.lineWork(lineList, pointList, RM, connectionRefPnt, **kwargs)

                except AttributeError:
                    pass #for travers where no target exists

    return lineList

def getIdFromSurvey(RM, survey, **kwargs):
    '''
    Gets the ID of the RM from the INstrument setup section of the land XML object
    :param RM: refPnt for RM
    :param survey: survey element from land xml file
    :return: ID
    '''

    #loop through survey subelements
    for child in survey.getchildren():
        if child.tag == kwargs["lxmlNamespace"] + "InstrumentSetup" and\
                child.find(kwargs["lxmlNamespace"]+"InstrumentPoint").values()[0] == RM:
                ID = child.get('id')
                break

    return ID

def getPntRefFromSurvey(ID, survey, **kwargs):
    '''
    Gets the refPnt of the RM from the Instrument setup section of the land XML object. Uses ID to find ref point.
    :param ID: ID of survey point
    :param survey: survey element from land xml file
    :return: refPnt
    '''

    #loop through survey subelements
    for child in survey.getchildren():
        if child.tag == (kwargs["lxmlNamespace"] + "InstrumentSetup") and child.get('id') == ID:
                refPnt = child.find(kwargs["lxmlNamespace"]+"InstrumentPoint").values()[0]
                break
    return refPnt





