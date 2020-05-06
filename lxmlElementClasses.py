
#classes to store linework
class curves(object):
    def __init__(self):
        self.rotation = []
        self.radius = []
        self.startRef = []
        self.startE = []
        self.startN = []
        self.centRef = []
        self.centE = []
        self.centN = []
        self.endRef = []
        self.endE = []
        self.endN = []
        self.layerName = []
        self.startAngle = []
        self.endAngle = []

#classes to store linework
class lines(object):
    def __init__(self):
        self.startRef = []
        self.startE = []
        self.startN = []
        self.endRef = []
        self.endE = []
        self.endN = []
        self.layerName = []
        self.colourCode = []

class parcels(object):
    def __init__(self):
        self.Name = []
        self.AreaRotation = [] #if a parcel its the Area, road its the orientation of the road
        self.centerRef = []
        self.centerRefE = []
        self.centerRefN = []
        self.landType = []

class points(object):
    def __init__(self):
        self.pntRef = []
        self.pntE = []
        self.pntN = []
        self.pntCodeName = []
        self.layerName = []
        self.colourCode = []