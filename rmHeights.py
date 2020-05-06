'''
Reads the json data file with survey mark info\

Finds survey mark based on type and number

Checks for mark status and AHD class.

If the mark exists and has AGD class not U. Height is returned.

"SurveyMarkGDA2020.json" must be in working directory.

'''
import json
from lxml import etree

class getSurveyMarks:

    '''
    retrieves survey marks from json file. This is so the file is only loaded once.
    Data is filtered for PMs and SSMs and put in an etree element for easier querying

    '''

    def __init__(self, ScimsFile):
        '''

        :param ScimsFile: JSON file with Scims data
        '''

        #f = "SurveyMarkGDA2020.json"
        with open(ScimsFile[0]) as json_file:
            data = json.load(json_file)

        self.scims = self.getFeatures(data)

    def getFeatures(self, data):
        '''
        retrieves the feature dictionary from the json file.
        This is the root attribute with RMs
        PMs and SSMs taken from feature dictionary and put into an etree element
        :param data:
        :return:
        '''

        features = data.get('SurveyMark').get("features")
        #create etree element
        scims = etree.Element("Scims")

        #extract PMs and SSMs and add to etree element
        scims = self.populateDataTree(scims, features)

        return scims

    def populateDataTree(self, scims, features):
        '''
        loops through feature items and retrieves data and adds to etree element (scims)
        :param scims:
        :param features:
        :return:
        '''

        for feat in features:
            props = feat.get('properties')
            if props.get("marktype") == 'SS' or props.get("marktype") == 'PM':
                # add RM name attribute
                mark = props.get("marktype") + str(props.get('marknumber'))
                RM = etree.SubElement(scims, mark)

                # add mark status
                markStatus = etree.SubElement(RM, "markstatus")
                if props.get("markstatus") == None:
                    markStatus.text = "None"
                else:
                    markStatus.text = props.get("markstatus")

                # add AHD class
                ahdClass = etree.SubElement(RM, "ahdclass")
                ahdClass.text = props.get("ahdclass")
                # add AHD height
                ahdHeight = etree.SubElement(RM, "ahdheight_label")
                ahdHeight.text = props.get("ahdheight_label")
                # add MGA Easting
                mgaE = etree.SubElement(RM, "mgaeasting_label")
                mgaE.text = props.get("mgaeasting_label")
                # add MGA Northing
                mgaN = etree.SubElement(RM, "mganorthing_label")
                mgaN.text = props.get("mganorthing_label")
                # add combined scaled factor
                mgaCSF = etree.SubElement(RM, "mgacsf2020_label")
                mgaCSF.text = str(props.get("mgacsf2020_label"))

        return scims

class surveyMarkHeights:

    def __init__(self, rmNumber, rmType, scims):
        '''

        :param rmNumber: integer
        :param rmType: sting -> PM or SS
        :param scims: etree element with condensed RM info
        '''

        #####################
        # get mark info
        self.RM, self.classAHD, self.heightAHD = self.getMarkInfo(scims.scims, rmNumber, rmType)

    def getMarkInfo(self, scims, rmNumber, rmType):
        '''
        searches feature dictionary to find survey marks.
        :param scims:
        :param rmNumber:
        :param rmType:
        :return:
        '''

        #set mark name
        markName = rmType + rmNumber

        #retrieve mark element
        markElem = scims.find(markName)

        #check mark status and create RM label
        if markElem.find("markstatus").text == "None":
            RM = rmType + str(rmNumber)
        else:
            RM = rmType + str(rmNumber) + markElem.find("markstatus").text

        #Check AHD class and add height to heightAHD
        classAHD = markElem.find('ahdclass').text
        if classAHD == "U" or classAHD == "E":
            heightAHD = None
        else:
            heightAHD = markElem.find("ahdheight_label").text

        return RM, classAHD, heightAHD


if __name__ == "__main__":
    #RM number

    markType = ["SS", "PM", "SS", "SS", "SS"]
    rmNum = [121497,32972, 58761, 206037, 206038]

    for i, mark in enumerate(markType):
        num = rmNum[i]
        #find rm in json file
        for feat in features:
            props = feat.get('properties')
            if props.get('marknumber') == num and props.get("marktype") == mark:
                break
        #print mark details
        print("RM: " + mark + str(num))
        if props.get("markstatus") == None:
            print("Mark Status: None")
        else:
            print("Mark Status: " + props.get("markstatus"))
        print("MGA combined scale factor: " + str(props.get("mgacsf2020_label")))
        print("MGA Easting: " + props.get("mgaeasting_label"))
        print("MGA Northing: " + props.get("mganorthing_label"))
        print("AHD class: " + props.get("ahdclass"))
        print("AHD height: " + props.get("ahdheight_label"))
        print("_____________________________")
        print("")
