'''
writes a dxf file from entities (lines, arcs, text items)
creates a point list saved to csv (so codes can be added to reference marks
'''

import ezdxf
import numpy as np
import rmHeights
import os

def main(lines, curves, text, points, **kwargs):
    '''
    creates a dxf instance and adds entities before saving
    :param lines: list of lines to be written to the dxf instance
    :param curves: list of arcs to  be written
    :param text: list of text items to be written to dxf. Contains lot info and road names
    :param points: RM marks to be written to csv file.
    :return:
    '''

    message=[]

    #create dxf instance
    dxf = ezdxf.new('AC1018')
    modSpace = dxf.modelspace()

    #create layers
    dxf = dxf_layers(points, dxf)
    # write RMs to csv file and create RM layer
    RMs, message = write_Rms_to_csv(points, **kwargs)
    message.append(str(RMs) + " RMs written")
    #dxf.layers.new(name='REFERENCE MARKS')

    #add lines, arcs and text
    if len(lines.startE) > 0:
        modSpace, items = dxf_lines(lines, modSpace)
        message.append(str(items) + " lines written")

    if len(curves.startE) > 0:
        modSpace, items = dxf_arcs(curves, modSpace)
        message.append(str(items) + " arcs written")

    if len(text.landType) > 0:
        modSpace, items = dxf_text(text, modSpace, **kwargs)
        message.append(str(items) + " text items written")

    #save dxf
    dxf.saveas(kwargs["outputPath"] + "\\" + kwargs['DP'] + '.dxf')

    return message


def dxf_layers(points, dxf):
    '''
    adds layers to dxf instance
    :param points: point list containing layer names
    :return: layers instance
    '''

    layers = np.unique(points.layerName)

    for layer in layers:
        dxf.layers.new(name=layer)

    return dxf

def dxf_lines(lines, modSpace):
    '''
    Adds line entities to dxf 
    :param lines:lines instance (contains line info)
    :param modSpace: 
    :return: 
    '''
    
    #loop through lines and add to dxf.
    for i, startE in enumerate(lines.startE):
        modSpace.add_line((startE, lines.startN[i]), (lines.endE[i], lines.endN[i]),
                     dxfattribs={'layer': lines.layerName[i]})
        
    return modSpace, i

def dxf_arcs(arcs, modSapce):
    '''
    Adds arc entities to dxf 
    :param arcs: arcs instance (contains arc info). All required info for dxf in arc objects
    :param modSapce: 
    :return: 
    '''
    
    #loop through arcs and add to dxf
    for i, radius in enumerate(arcs.radius):
        #print("i = " +str(i))
        #print("layer = " + arcs.layerName[i])
        modSapce.add_arc((arcs.centE[i], arcs.centN[i]), radius, arcs.startAngle[i], arcs.endAngle[i],
                     dxfattribs={'layer': arcs.layerName[i]})
        
    return modSapce, i

def dxf_text(text, modSapce, **kwargs):
    '''
    Adds text entities to dxf. Text contains both parcel info and road labels 
    :param text: text instance
    :param modSapce: 
    :return: 
    '''

    for i in range(0, len(text.Name), 1):
        if text.landType[i] == "Parcel":
            mtext = modSapce.add_mtext(kwargs["DP"], dxfattribs={'layer': "TEXT", 'style': 'OpenSans'})
            mtext.text += "\nLOT" + text.Name[i] + "\n"
            mtext.text += text.AreaRotation[i] + "m2"
            mtext.set_location((text.centerRefE[i], text.centerRefN[i]), 0, 5)
            mtext.set_color('red')
        else:  # Road label
            mtext = modSapce.add_mtext(text.Name[i], dxfattribs={'layer': "TEXT", 'style': 'OpenSans'})
            mtext.set_location((text.centerRefE[i], text.centerRefN[i]), 0, 5)
            mtext.set_color('red')

    return dxf_text, i

def write_Rms_to_csv(points, **kwargs):
    '''
    write RMs to csv file
    :param RMs:
    :param kwargs:
    :return:
    '''

    #message string to write to program output
    message = []
    #retrieve Scims height data from json file if required
    #if kwargs["rmHeights"]:
    #    scims = rmHeights.getSurveyMarks(kwargs["ScimsFile"])
    if not os.path.exists(kwargs["outputPath"]):
        os.mkdir(kwargs["outputPath"])

    f = open((kwargs["outputPath"] + "\\"+kwargs["DP"]+".csv"), 'w')
    RMs = 0
    #print("Data length: " + str(len(points.pntE)))
    #print("Code Name length: " + str(len(points.pntCodeName)))
    print("")
    for i, E in enumerate(points.pntE):
        if points.layerName[i] == 'REFERENCE MARKS':
            heightAHD = None
            #get heights if required
            if kwargs["rmHeights"]:
                #print(points.pntCodeName[i])
                if points.pntCodeName[i][0:2] == 'PM' or points.pntCodeName[i][0:3] == 'SSM':
                    if points.pntCodeName[i][0:2] == 'PM':
                        rmNumber = points.pntCodeName[i][2:]
                        rmType = 'PM'
                    else:
                        rmNumber = points.pntCodeName[i][3:]
                        rmType = 'SS'

                    RM = rmHeights.surveyMarkHeights(rmNumber, rmType, kwargs["scimsData"])
                    message.append(points.pntCodeName[i] + ":\tClass=" + RM.classAHD + "\t\tAHD Height=" + str(RM.heightAHD))
                    heightAHD = RM.heightAHD

            if heightAHD == None:
                line = str(i + 1) + "," + str(E) + "," + str(points.pntN[i]) + \
                        ",," + points.pntCodeName[i] + "," + points.layerName[i] + "\n"
            else: #if has a height to add
                line = str(i + 1) + "," + str(E) + "," + str(points.pntN[i]) + ',' + \
                       RM.heightAHD + "," + RM.RM + "," + points.layerName[i] + "\n"
            f.write(line)
            RMs+=1

    if len(message) > 0:
        message.append("")

    f.close()

    return RMs, message