'''
#v1.2 - no MXL functionality. Landxml converted to DXF.


'''

from lxml import etree
import lxmlElementClasses as ElemClasses
import parcelProcessor
import referenceMarks as RM
import glob
import dxf_writer as dxf
import rmHeights

def main(**kwargs):

    # set lxmlObj
    lxmlObj = etree.parse(kwargs["lxmlFile"])
    kwargs['lxmlObj'] = lxmlObj
    
    # get DP from land XML
    kwargs["DP"] = getDP(**kwargs)

    #get class instances
    parcelList = ElemClasses.parcels()
    pointList = ElemClasses.points()
    rmList = ElemClasses.points()
    lineList = ElemClasses.lines()
    curveList = ElemClasses.curves()

    #get land parcels, easements and roads
    parcelList, pointList, lineList, curveList = parcelProcessor.main(parcelList, pointList, lineList,
                                                                      curveList, **kwargs)

    #get RM marks are their connections
    pointList, lineList, kwargs["lxmlObj"] = RM.main(pointList, lineList, **kwargs)

    #get additional CG points for connections
    #pointList, lineList = CgPoints.main(pointList, lineList, **kwargs)




    message = dxf.main(lineList, curveList, parcelList, pointList, **kwargs)


    return message


def getDP(**kwargs):
    '''
    retrieves DP from land XML
    :param kwargs:
    :return:
    '''

    #find survey element and get DP number from SurveyHeader subelement
    for child in kwargs["lxmlObj"].find(kwargs["lxmlNamespace"] + "Survey").getchildren():
        if child.tag == (kwargs["lxmlNamespace"] + "SurveyHeader"):
            DP = "DP" + child.get("name")

    return DP


if __name__ == "__main__":
    path = "d:\\UAVsInGreenfields\\Code\\landXML\\"
    lxmlNamespace = "{http://www.landxml.org/schema/LandXML-1.2}"
    output = 'dxf'
    outputPath = "output"
    AHD = True

    if AHD:
        scimsData = rmHeights.getSurveyMarks('d:\\UAVsInGreenfields\\Code\\landXML_Converter\\SurveyMarkGDA2020.json')
    else:
        scimsData = None

    fileList = glob.glob("d:\\UAVsInGreenfields\\Code\\landXML\\input\\*.xml")
    for f in fileList:
        lxmlFile = 'd:\\UAVsInGreenfields\\Code\\landXML\\input\\dp1135271p.xml'
        print("processing Land XML: "+'dp1135271p.xml')
        kwargs = dict(path = path,
                      lxmlFile = lxmlFile,
                      layer = "",
                      code = "",
                      lxmlNamespace = lxmlNamespace,
                      outputType = output,
                      outputPath=outputPath,
                      rmHeights=AHD,
                      ScimsFile='SurveyMarkGDA2020.json',
                      scimsData=scimsData)

        message = main(**kwargs)
        for mes in message:
            print(mes)
        print("")
        print("___________________________")
        break