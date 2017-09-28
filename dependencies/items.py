"""
The series of items that may be used by the NR9 robot
"""


class Needle(object):
    def __init__(self, gauge, length):
        """a class object defining a disposable needle"""
        if type(gauge) != int:
            raise ValueError('The gauge must be an integer value')
        self.gauge = gauge
        from PyNR.dependencies.miscellaneous import gauges  # dictionary of needle gauges
        self.od = gauges[gauge]  # outer diameter

        self.length = length  # length of the needle
        self.contaminated = False  # whether the needle has been contaminated

    def __repr__(self):
        return "%s(%d gauge)" % (self.__class__.__name__, self.gauge)

    def __str__(self):
        return "%d gauge needle" % self.gauge


class PipetteTip(object):
    def __init__(self, properties={}, location=None):
        """A class object defining a pipette tip"""
        self.properties = {
            'size': [40., 5.],  # the length and diameter of the pipette tip in mm
            'volume': 1.25,  # the maximum volume of the pipette tip in mL
        }
        self.properties.update(properties)  # updates default keywords as specified
        self.location = location
        self.contaminated = False

    def __repr__(self):
        return "%s(%s mL)" % (self.__class__.__name__, self.properties['volume'])

    def __str__(self):
        return "%s mL pipette tip" % self.properties['volume']


class Vial(object):
    def __init__(self, name, vialproperties={}, contents={}, location=None):
        """
        A class defining screw-capped vials and the various 
        properties that need to be associated with them. 
        """
        self.contents = {}  # to store the vial contents
        self.contents.update(contents)

        self.p = {  # physical properties of the vial (see vialprofiles.py for details)
            'capdiameter': None,
            'crimp': False,
            'diameter': 11.62,
            'height': 33.41,
            'screw': True,
            'piercediameter': None,
            'pitch': 1.07,
            'rotations': 2,
        }
        self.p.update(vialproperties)

        if self.p['crimp'] == self.p['screw'] or not self.p['screw'] and not self.p['crimp']:
            raise ValueError('Only one of crimp or screw may (and must) be true. Crimp: %s, Screw: %s' % (
                self.p['crimp'], self.p['screw'])
                )
        import numpy
        self.location = location  # location
        # TODO convert location from dict to list then to array
        self.alocation = numpy.asarray([location['x'], location['y']])  # array location
        self.name = name  # the name identifier for this vial
        self.tstart = None  # reaction start time
        self.tquench = None  # reaction quench time
        self.capped = True  # whether the cap is installed

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.name)

    def __str__(self):
        return "Vial %s" % self.name

    def generate_piercearray(self, needle=None, **kwargs):
        """
        Generate a PierceArray object for needle piercing
        See miscellaneous.PierceArray for keyword argument details
        
        required keyword arguments:
            one of needle, gauge, or diam
            if piercediameter was not set on Vial instance initialization, it must be set here
        """
        if needle is not None:
            kwargs['needle'] = needle
        if 'piercediameter' in kwargs:
            self.p['piercediameter'] = kwargs['piercediameter']
            del kwargs['piercediameter']

        from PyNR.dependencies.miscellaneous import PierceArray
        self.pa = PierceArray(
            piercediameter=self.p['piercediameter'],
            **kwargs
        )

    def get_piercelocation(self):
        """retrieves a needle pierce location from the piercearray"""
        if 'pa' not in self.__dict__:
            raise KeyError('A pierce array has not been created for this vial instance')
        return self.alocation + self.pa.getloc()
        # TODO update when PierceArray alloweduses is functioning
        """
        try: # returns the location
            return self.location + self.pa.getloc()
        except self.pa.MaxPierces: # if the maximum number of pierces has been reached, ask if the user wants to reuse holes
            a = input('The maximum number of pierces for this pierce array has been reached (%d)\nDo you wish to reuse pierce holes? Y/N ' %(len(self.pa)))
            if a.lower() in ['y','yes']:
                self.pa.kw['alloweduses'] += 1
                return self.pa.getloc() # returns the location
            else:
                raise self.pa.MaxPierces
        """


# if __name__ == '__main__':
# nd1 = Needle(
#     18, # gauge
#     2.45 # length
#     )
# pt1 = PipetteTip(
#     )
#
# v1 = Vial(
#     'A1',
#     contents = {'a':1},
#     vialproperties = profiles['HPLC1mLpierce'],
#     location = [100.,100],
#     )
