from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QFileDialog
from landXML_ProcessorFrontEnd import Ui_LandXMLProcessor
import sys
import glob
import os

import landXML_Converter as converter
import rmHeights

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()

        self.ui = Ui_LandXMLProcessor()
        self.ui.setupUi(self)

        # variables
        self.dir = 'c:\\'
        self.batch = "no"
        self.Scims = False
        self.fileList = "" #list of files to be converted
        #ADD WHITE SPACE TO PROGRAM OUTPUT
        self.ui.txtEdit_ProgramProgress.addItem('PROGRAM OUTPUT')
        self.ui.txtEdit_ProgramProgress.addItem('----------------------- ')
        self.ui.txtEdit_ProgramProgress.addItem('')

        # File to convert or Directory where input data exists. If radBut_BatchProcess selected will request a directory
        self.ui.pBut_BrowseInput.clicked.connect(self.inputDir)

        # Batch Process Radio Button
        self.ui.radBut_BatchProcess.toggled.connect(self.radBut_BatchProcess_clicked)

        # Output Directory
        self.ui.pBut_BrowseOutput.clicked.connect(self.outputDir)

        # SCIMS - include RM heights radio button
        self.ui.radBut_Scims.toggled.connect(self.radBut_Scims_clicked)

        #convert land xml files to MXL button
        self.ui.pBut_convertFiles.clicked.connect(self.convertLandXML)

    ###############################
    # routines called when from button clicks
    def inputDir(self):
        '''
        sets directory opened when searching for files when batch procces radio button selected
        Used to select file to convert from landXML to MXL
        '''
        if self.batch == "yes": #if batch processing is selected
            self.inputPath = str(QFileDialog. \
                                getExistingDirectory(self, 'Select input file directory:', self.dir))
            self.ui.lineEdit_InputTxt.setText(self.inputPath)

            #enter program text
            self.ui.txtEdit_ProgramProgress.addItem('BATCH PROCESS ENABLED')
            self.ui.txtEdit_ProgramProgress.addItem('-------------------------------------------')
            self.ui.txtEdit_ProgramProgress.addItem('')
            #write input directory
            self.ui.txtEdit_ProgramProgress.addItem('Input directory:')
            self.ui.txtEdit_ProgramProgress.addItem('> '+self.inputPath)
            self.flst = glob.glob(self.inputPath+"\\*.xml")
            #writye files to be converted
            self.ui.txtEdit_ProgramProgress.addItem('> '+str(len(self.flst)) + ' files selected to be converted...')
            self.ui.txtEdit_ProgramProgress.addItem('')

            #if len(self.flst) > 0:
                #for f in self.flst:
                 #   self.ui.txtEdit_ProgramProgress.addItem(f.replace(self.inputDir, ""))
            #else:
            if len(self.flst) == 0:
                self.ui.txtEdit_ProgramProgress.addItem('> '+"No XML files in " + self.inputPath)

        else: #for single file

            #select a file of xml type
            dialog = QFileDialog(self)
            dialog.setFileMode(QFileDialog.ExistingFile)
            dialog.setNameFilter("XML files (*.xml)")
            dialog.selectNameFilter("XML files (*.xml)")
            #dialog.setDirectory(self.dir)
            if dialog.exec_():
                self.file = dialog.selectedFiles()

            self.flst = [self.file[0]]

            #Program progress output
            self.ui.lineEdit_InputTxt.setText(self.file[0])
            self.ui.txtEdit_ProgramProgress.addItem('SINGLE FILE SELECTED FOR CONVERSION')
            self.ui.txtEdit_ProgramProgress.addItem('-------------------------------------------')
            self.ui.txtEdit_ProgramProgress.addItem('')
            self.ui.txtEdit_ProgramProgress.addItem('> '+self.file[0] + " selected")
            self.inputPath = os.path.dirname(os.path.abspath(self.file[0]))
            self.ui.txtEdit_ProgramProgress.addItem('')
            self.ui.txtEdit_ProgramProgress.addItem('')



        # update working dirfectory
        self.dir = str(self.inputPath)
        self.outputPath = self.inputPath
        self.ui.lineEdit_OutputDir.setText(self.outputPath)

    ###############################
    # routines called from button clicks
    def outputDir(self):
        '''
        sets directory output directory where converted files will be stored
        '''
        self.outputPath = str(QFileDialog. \
                            getExistingDirectory(self, 'Select output directory:', self.dir))
        self.ui.lineEdit_OutputDir.setText(self.outputPath)

    def radBut_BatchProcess_clicked(self, enabled):
        '''
        sets whether maps should have the centre pivot cut out
        '''
        if enabled:
            self.batch = 'yes'
        else:
            self.batch = 'no'

    def radBut_Scims_clicked(self, enabled):
        '''
        sets whether to add heights of RMs
        '''
        if enabled:
            self.Scims = True
        else:
            self.Scims = False

    #function to call program to convert landXML
    def convertLandXML(self):
        '''
        loops through files in self.flst and converts them to MXL
        :return:
        '''
        lxmlNamespace = "{http://www.landxml.org/schema/LandXML-1.2}"
        #namespace for MXL - not used
        #mxlTemplate = "template.mxl"
        #mxlNamespace = '{tps}'

        #get scims file
        if self.Scims:

            #select a file of json type
            dialog = QFileDialog(self)
            dialog.setFileMode(QFileDialog.ExistingFile)
            dialog.setNameFilter("JSON files (*.json)")
            dialog.selectNameFilter("JSON files (*.json)")
            #dialog.setDirectory(self.dir)
            if dialog.exec_():
                ScimsFile = dialog.selectedFiles()
            self.ui.txtEdit_ProgramProgress.addItem('Scims File selected: '+ScimsFile[0])
            self.ui.txtEdit_ProgramProgress.addItem('Heights will be added to RMs where AHD class better than E.')
            self.ui.txtEdit_ProgramProgress.addItem('')
            scimsData = rmHeights.getSurveyMarks(ScimsFile)
        else:
            ScimsFile = None
            scimsData = None

        #print("Past Scims load")
        #write error message if no files selected
        if len(self.flst) == 0:
            self.ui.txtEdit_ProgramProgress.addItem('No Land XML files selected.')
            self.ui.txtEdit_ProgramProgress.addItem('Select a directory with land XML files or')
            self.ui.txtEdit_ProgramProgress.addItem('a select a land XML file.')
        else:
            for f in self.flst:
                self.ui.txtEdit_ProgramProgress.addItem('Converting: ' + f)
                self.ui.txtEdit_ProgramProgress.addItem('')
                #create kwargs to send to converter function
                kwargs = dict(path=self.inputPath,
                              outputPath=self.outputPath,
                              lxmlFile=f,
                              layer="",
                              code="",
                              lxmlNamespace=lxmlNamespace,
                              outputType='dxf',
                              rmHeights=self.Scims,
                              scimsData=scimsData)

                message = converter.main(**kwargs)
                for mes in message:
                    self.ui.txtEdit_ProgramProgress.addItem(mes)

                self.ui.txtEdit_ProgramProgress.addItem('')
                self.ui.txtEdit_ProgramProgress.addItem('-----------------------------------')



def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()