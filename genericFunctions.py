'''
Author: S Parkes
Date: 5/12/19
Version: 1.0

Generic Functions Used throughout program
'''

import numpy as np

def calcLineEquation(E1, E2, N1, N2):
    '''
    calculates equation of parcel bdy line from two points
    :param E1:
    :param E2:
    :param N1:
    :param N2:
    :return: m, b
    '''

    if (E2-E1) == 0:
        b = E2 # here b is x-intercept
        m = np.inf
    elif (N2-N1) == 0:
        m = 0
        b = N2
    else:
        m = (N2-N1)/(E2-E1)
        b = N1 - m*E1

    return m, b

def calcIntersectionPoint(m1, b1, m2, b2):
    '''
    Calculate intersection coordinates between 2 lines
    :param m1:
    :param b1:
    :param m2:
    :param b2:
    :return: E, N
    '''

    if (m1-m2) == 0:
        E = 0
        N = 0
    elif m1 == np.inf:
        E = b1
        N = E*m2 + b2
    elif m2 == np.inf:
        E = b2
        N = E*m1 + b1
    else:
        E = (b2-b1)/(m1-m2)
        N = E*m1 + b1

    return E, N

def calcBearing(startE, startN, endE, endN):
    '''
    calculates bearing of a line from 2 points
    :param startE:
    :param startN:
    :param endE:
    :param endN:
    :return:
    '''



    if endN > startN and endE > startE:
        angle = np.degrees(np.arctan((endN - startN) / (endE - startE)))
        bearing = 90 - angle
    elif endN < startN and endE > startE:
        angle = -np.degrees(np.arctan((endN - startN) / (endE - startE)))
        bearing = 90 + angle
    elif endN < startN and endE < startE:
        angle = np.degrees(np.arctan((endN - startN) / (endE - startE)))
        bearing = 270 - angle
    elif endN > startN and endE < startE:
        angle = -np.degrees(np.arctan((endN - startN) / (endE - startE)))
        bearing = 270 + angle
    elif endN == startN and endE > startN:
        bearing = 90.00
    elif endN == startN and endE < startN:
        bearing = 270.00
    elif endN > startN and endE == startN:
        bearing = 0.0
    else:
        bearing = 180.0

    return bearing

def bearing2slope(bearing):
    '''
    converts bearing of line to a slope
    :param bearing:
    :return:
    '''

    if bearing < 90:
        angle = 90 - bearing


    return slope




if __name__ == "__main__":

    #file IO
    path = "d:\\UAVsInGreenfields\\DP1252867_MossVale\\"
    file = "DP1252867.xml"

    schema = "{http://www.landxml.org/schema/LandXML-1.2}" #annoying bit at start of element tags

    #info for json file to save property info
    DP = "DP1252867"
    TotalLots = 40
    fieldNotes ={"KerbType": "standard",
                 "TotalLots": TotalLots}
    json_ds = {DP: {"fieldNotes": fieldNotes,
                    "Parcels": {}}}
    #list of lots to be processed
    lotList = np.arange(1,(TotalLots+1),1)

    #dictonary to send arguments to xml processor
    kwargs = {"path" : path,
              "file" : file,
              "schema" : schema,
              "DP": DP,
              "lotList" : lotList,
              "json": json_ds}

    json_ds = main(**kwargs)