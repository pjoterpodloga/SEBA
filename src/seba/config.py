class SebaConfig:

    def __init__(self, name=None, control=None, tb=None, corners=None, 
                 script=None, plot=None, meas=None, extraction=None):
        self.name = name
        self.control = control
        self.tb = tb
        self.corners = corners
        self.script = script
        self.plot = plot
        self.meas = meas
        self.extraction = extraction