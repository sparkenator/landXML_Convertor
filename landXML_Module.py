'''
Author: S Parkes

Version: 1.0
Date 18/02/2020

Collection of functions to analyse and collect data from land XML files.
Uses python lxml.etree module
'''

from lxml import etree

class landXML_loader:

    def __init__(self, landXML_file):
        '''
        Loads land XML elements into class attribute
        A attribute is created for each element:
            - CgPoints
            - Parcels
            - Survey
            - Monuments

        :param landXML_file: land XML file to be loaded. Needs to include path in filename
        '''

        #land XML namespace
        self.landXML_namespace = "{http://www.landxml.org/schema/LandXML-1.2}"
        #parse land XML file into an etree element
        landXML_obj = etree.parse(landXML_file)
        #create attributes
        self.CgPoints = landXML_obj.find(self.landXML_namespace + "CgPoints")
        self.Parcels = landXML_obj.find(self.landXML_namespace + "Parcels")
        self.Survey = landXML_obj.find(self.landXML_namespace + "Survey")
        self.Monuments = landXML_obj.find(self.landXML_namespace + "Monuments")

        self.DP = self.getDP_number(self.Survey, self.landXML_namespace)

    def getDP_number(self, survey, namespace):
        '''
        retrieves the DP number from landXML file
        :param landXML_obj: survey object of landXML file
        :return: DP. DP number
        '''

        # find survey element and get DP number from SurveyHeader subelement
        for child in survey.getchildren():
            if child.tag == (namespace + "SurveyHeader"):
                DP = "DP" + child.get("name")

        return DP


class parcelVertexes:

    def __init__(self, landXML):
        '''
        Gets the parcel vertex coordinates from landXML.Parcel object
        Stores them in attributes as lists
        :param parcels: landXMLobject
        '''

        self.pntRef = []
        self.Easting = []
        self.Northing = []
        self.Elevation = []

        # loop through parcels in landXML
        for parcel in landXML.Parcels.getchildren():
            # check it is a proposed lot for the subdivision
            if parcel.get("class") == "Lot" and parcel.get("state") == "proposed":
                # loop through line work of parcel
                for lineItem in parcel.find(landXML.landXML_namespace + "CoordGeom").getchildren():
                    # get ref numbers for start end of lines
                    startRef = lineItem.find(landXML.landXML_namespace + "Start").values()[0]
                    endRef = lineItem.find(landXML.landXML_namespace + "End").values()[0]

                    # check ref points not in lists already and then add
                    if startRef not in self.pntRef:
                        Easting, Northing = getCoords(startRef, landXML)
                        self.pntRef.append(startRef)
                        self.Easting.append(Easting)
                        self.Northing.append(Northing)
                        self.Elevation.append("")
                    if endRef not in self.pntRef:
                        Easting, Northing = getCoords(endRef, landXML)
                        self.pntRef.append(endRef)
                        self.Easting.append(Easting)
                        self.Northing.append(Northing)
                        self.Elevation.append("")


def getCoords(pntRef, landXML):
    '''
    gets coordinates of pntRef from landXML CG points
    :param pntRef: point reference in CG points of landXML file
    :return: East, North
    '''

    # get coordinates of SSM 'X'
    for child in landXML.CgPoints.getchildren():
        if child.get("name") == pntRef:
            East = float(child.text.split(' ')[1])
            North = float(child.text.split(' ')[0])

    return East, North