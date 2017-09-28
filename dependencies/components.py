"""
The series of components that may be installed on or off the NR9 bed

"""


class Container(object):
    def __init__(self, pt, conttype='100beaker', dimensions=None):
        """
        A liquid container (e.g. beaker or Erlenmeyer) which supplies 
        sample or solvent to the robot
        """
        # modify this so that the pt tray is no longer required or necessary
        # the tips and drawing should be handled by the script or components in the head class

        if isinstance(pt, PipetteTray) is False:  # checks that it was handed a PipetteTray instance
            raise TypeError('A Container object must be handed a PipetteTray instance')
        self.pt = pt  # store the pipette tray instance

        presets = {  # dimensions for containers in mm
            #  for beakers, the diameter and current amount are required
            '50beaker': {'d': 4.0, 'cont': 50.0},  # 50 mL beaker
            '100beaker': {'d': 5.0, 'cont': 100.0},  # 100 mL beaker
            '150beaker': {'d': 6.0, 'cont': 150.0},  # 150 mL beaker
            '250beaker': {'d': 7.0, 'cont': 250.0},  # 250 mL beaker
            '400beaker': {'d': 8.0, 'cont': 400.0},  # 400 mL beaker
            '600beaker': {'d': 9.0, 'cont': 600.0},  # 600 mL beaker
            '1000beaker': {'d': 10.0, 'cont': 1000.0},  # 1000 mL beaker
            '2000beaker': {'d': 13.0, 'cont': 2000.0},  # 2000 mL beaker

            # is it worth profiling other types of flask? 
            # what are most likely to be used in these applications? 
        }
        if dimensions is None:
            self.dimensions = presets[conttype]
        else:
            self.dimensions = dimensions
        self.conttype = conttype
        import math
        self.pi = math.pi
        if conttype.endswith('beaker'):
            self.volume = self.dimensions['cont']

        # tells the container object whether the current pipette tip was used for this container
        # if this is true, the draw function will use the same pipette tip for multiple draws
        # if this is false, it will retrieve a new tip
        self.activetip = False

    def height(self):
        """
        calculates the height from the dimensions and current volume
        returns height in cm
        """
        if self.conttype.endswith('beaker'):
            return self.volume / (self.pi * ((self.dimensions['d'] / 2.) ** 2))


class PipetteTray(object):
    def __init__(self, **kwargs):
        """
        A class object defining a pipette tip holding Tray
        It is assumed that the tray will be completely populated at the start of the run
        """
        self.kw = {
            'center': [250., 250.],  # the center of the Tray in mm(across,down)
            'tiparray': [12, 4],  # the arrangement of the pipette tips in the Tray (across, down)
            'center-center': 6.0,  # distance center to center of the vials in the Tray in mm
            'tipproperties': {},  # any special pipette tip properties
        }
        self.kw.update(kwargs)  # updates default keywords as specified
        self.array = self.createarray(self.kw['tiparray'])  # creates the pipette array
        self.generatorarray = self.yieldtip()  # creates a generator

    def createarray(self, size):
        """ creates a flattened array of pipette tips with location information"""
        x, y = size
        from PyNR.dependencies.items import PipetteTip
        import numpy as np
        a = lambda z: [PipetteTip(properties=self.kw['tipproperties']) for i in range(z)]
        array = [a(val) for val in range(y)]
        # creates a location array based on the sizing and spacing parameters provided to the class
        xlocs = np.linspace(0., (x - 1) * self.kw['center-center'], x)  # create spacing array
        xlocs -= max(xlocs) / 2.  # correct for center of plate
        xlocs += self.kw['center'][0]  # align to position of plate
        ylocs = np.linspace(0., (y - 1) * self.kw['center-center'], y)
        ylocs -= max(ylocs) / 2.
        ylocs += self.kw['center'][1]
        for row, val1 in enumerate(array):
            for col, val2 in enumerate(val1):
                array[row][col].location = [xlocs[col], ylocs[-row]]
        return [item for sublist in array for item in sublist]  # flattens the array

    def yieldtip(self):
        """grabs the location of the next pipette tip"""
        for tip in self.array:
            yield tip

    class TrayEmpty(Exception):
        def __init__(self):
            """custom exception to indicate that this tray is empty"""
            super(PipetteTray.TrayEmpty, self).__init__("The tray does not contain any more pipette tips")

    def gettip(self):
        """retrieves the next pipette tip from the generator"""
        try:
            return next(self.generatorarray)  # try to return the next pipette tip
        except StopIteration:
            raise self.TrayEmpty  # if at the end of the array, raise empty execption


class SyringePump(object):
    def __init__(self, **kwargs):
        """
        A class object defining a syringe pump and how to talk with it
        """
        self.kw = {
            'flowrate': 10.,  # desired flowrate
            'mode': 'push',  # 'push' or 'pull'
            'diam': 3.125,  # syringe inner diameter in mm
            'running': False,  # whether the pump is active
        }
        self.kw.update(kwargs)
        self.time = __import__('time')
        self.active = {'inject': [], 'withdraw': []}  # dictionary of active times of the pump

    def changerate(self, newrate):
        """changes the flow rate"""
        # trigger communication
        self.kw['flowrate'] = newrate
        if self.kw['running'] is True:
            self.timepoint('stop')  # stop the previous time course
            self.timepoint('start')  # start it again with the new flowrate

    def changedirection(self):
        """changes the direction of flow"""
        if self.kw['running'] is True:
            self.timepoint('stop')
        dirs = ['push', 'pull']
        dirs.remove(self.kw['mode'])
        self.kw['mode'] = dirs[0]
        if self.kw['running'] is True:
            self.timepoint('start')

    def eta(self):
        """a method of estimating the time to completion"""
        pass

    def start(self):
        """tells the comms instance to start the pump"""
        # once the command is known, code this
        self.timepoint('start')
        self.kw['running'] = True

    def stop(self):
        """tells the comms instance to stop the pump"""
        # ditto here
        self.timepoint('stop')
        self.kw['running'] = False

    def timepoint(self, key):
        """sets a timepoint to track volumes"""
        if self.kw['mode'] == 'push':
            a = self.active['inject']
        else:
            a = self.active['withdraw']
        if len(a) == 0 or a[-1]['stop'] is not None:
            a.append({
                'start': None,
                'stop': None,
                'rate': float(self.kw['flowrate'])
            })
        a[-1][key] = self.time.time()


class VialTray(object):
    def __init__(self, population=None, **kwargs):
        """A class object defining a vial Tray"""
        # if isinstance(comms,communicator) is False: # checks that it was handed a communicator object
        #     raise TypeError('A SyringePump object must be handed a communicator object')
        # self.comms = comms
        self.population = population
        self.kw = {
            'size': [245., 165.],  # the physical size of the Tray in mm
            'center': [0., 231.],  # the center of the Tray in mm(across,down)
            'vialarray': [12, 8],  # the arrangement of the vials in the Tray (across, down)
            'center-center': 20.0,  # distance center to center of the vials in the Tray in mm
            'vialproperties': {},  # any special vial properties
            'iterorder': 'across',  # either across or down, will interate across first or down first respectively
            'vialbottoms': 23.87,  # the bottom of the vials (relative to the bed)
        }
        self.kw.update(kwargs)  # updates default keywords as specified
        from PyNR.dependencies.general import cellname_to_inds
        self.cti = cellname_to_inds
        self.vials = self.vialarray(self.kw['vialarray'])  # create an array for vials
        self.locarray = self.locationarray()  # store location values
        self.populate(self.population, self.locarray)

    def __iter__(self):
        """the instructions to iterate over each vial"""
        if self.kw['iterorder'] == 'across':
            for row in self.vials:
                for vial in row:
                    if vial is not None:  # check if vial slot is populated
                        yield vial
        elif self.kw['iterorder'] == 'down':
            for col in range(len(self.vials[0])):
                for row in range(len(self.vials)):
                    vial = self.vials[row][col]
                    if vial is not None:
                        yield vial

    def __getitem__(self, item):
        """returns the loation of the specified vial

        Can be either a string (e.g. 'A1') or a tuple
        """
        if type(item) == str:
            x, y = self.cti(item)
            return self.locarray[x][y]
        elif type(item) == tuple:
            return self.locarray[item[0]][item[1]]

    class CellEmpty(Exception):
        def __init__(self, vial):
            """raised if the selected vial cell is empty"""
            self.vial = vial
            super(VialTray.CellEmpty, self).__init__('The selected vial %s is defined as empty' % self.vial)

    def locationarray(self):
        """
        creates a location array based on the sizing and spacing parameters provided to the class

        The location array will have the same axes as the robot (see communicator.inverse_kinematics for details)
        """
        x, y = self.kw['vialarray']
        import numpy as np
        xlocs = np.linspace(0., (x - 1) * self.kw['center-center'], x)  # create spacing array
        xlocs -= max(xlocs) / 2.  # correct for center of plate
        xlocs += self.kw['center'][0]  # align to position of plate
        ylocs = np.linspace(0., (y - 1) * self.kw['center-center'], y)
        ylocs -= max(ylocs) / 2.
        ylocs += self.kw['center'][1]
        xlocs = np.flip(xlocs, 0)
        basearray = self.vialarray(self.kw['vialarray'])
        for row, val1 in enumerate(basearray):
            for col, val2 in enumerate(val1):
                basearray[row][col] = {  # define x,y,z location
                    'x': xlocs[col],
                    'y': ylocs[row],
                    'z': self.kw['vialbottoms'],
                }
        # TODO incorporate z location
        return basearray

    def populate(self, dct, locations):
        """ populates the vial array with the dictionary provided"""
        from PyNR.dependencies.items import Vial  # import the vial class
        for key in dct:  # for each vial
            row, col = self.cti(key)
            self.vials[row][col] = Vial(key,
                                        contents=dct[key],
                                        vialproperties=self.kw['vialproperties'],
                                        location=locations[row][col],
                                        )

    def recap(self, vialname):
        """re-caps the specified vial"""
        row, col = self.cti(vialname)
        vial = self.vials[row][col]
        # move to vial.location
        # recap the vial

    def uncap(self, vialname):
        """uncaps the specified vial"""
        row, col = self.cti(vialname)
        vial = self.vials[row][col]
        # move to vial.location
        # recap the vial

    def vialarray(self, size):
        """create an array to hold vial objects"""
        a = lambda x: [None for i in range(x)]
        return [a(size[0]) for i in range(size[1])]

# if __name__ == '__main__':
#     from PyNR.dependencies._communicator import communicator
#     from PyNR.dependencies.components import VialTray,SyringePump,PipetteTray,Container
#     comms = communicator(offline=True)
#
#     vialpop = {
#         'A1': {'MeOH':1., 'reagent1':0.5, 'reagent2':0.5, 'catalyst':0.005},
#         'C5': {'MeOH':1., 'reagent1':0.5, 'reagent2':0.5, 'catalyst':0.005},
#         'C6': {'MeOH':1., 'reagent1':0.5, 'reagent2':0.5, 'catalyst':0.005},
#         'F1': {'MeOH':1., 'reagent1':0.5, 'reagent2':0.5, 'catalyst':0.005},
#         'F8': {'MeOH':1., 'reagent1':0.5, 'reagent2':0.5, 'catalyst':0.005},
#         'H3': {'MeOH':1., 'reagent1':0.5, 'reagent2':0.5, 'catalyst':0.005},
#         }
#
#     VT1 = VialTray(
#         comms,
#         population = vialpop,
#         # iterorder = 'down',
#         )
#
#     SP1 = SyringePump(
#         comms
#         )
#
#     PT1 = PipetteTray(
#         # tiparray = [1,4]
#         )
#
#     cont = Container(
#         PT1
#         )
